import json
import semver
import sys
import os
from git import Repo
from lxml import etree
from git_changelog.cli import build_and_render
import subprocess

pathVersion = sys.argv[1]
stage = sys.argv[2]
type = sys.argv[3]

CI_PIPELINE_ID = os.environ.get('CI_PIPELINE_ID')
PERSONAL_ACCESS_TOKEN = os.environ.get('PERSONAL_ACCESS_TOKEN')
PRIVATE_ACCESS_REPO = os.environ.get('PRIVATE_ACCESS_REPO')
REPO_BRANCH_NAME = os.environ.get('REPO_BRANCH_NAME')

repo = Repo('.')
last_commit = repo.head.commit
last_commit_message = last_commit.message.lower()
remote = repo.remotes.origin

if type == 'npm':
    with open(pathVersion) as file:
        data = json.load(file)
        current_version = data['version']
        version_parts = semver.parse(current_version)

elif type == 'maven':
    tree = etree.parse(pathVersion)
    root = tree.getroot()
    namespace = {'ns': 'http://maven.apache.org/POM/4.0.0'}
    current_version = root.find('ns:version', namespaces=namespace)
    version_parts = semver.parse(current_version.text)

elif type == 'dotnet':
    tree = etree.parse(pathVersion)
    root = tree.getroot()
    current_version = root.find('PropertyGroup/Version')
    version_parts = semver.parse(current_version.text)

elif type == 'datapower':
    with open(pathVersion) as file:
        data = json.load(file)
        current_version = data['version']
        version_parts = semver.parse(current_version)

if current_version is None:
    print("Error: No se encontró el elemento de la versión en el archivo")
    sys.exit(1)

version_number = f"{version_parts['major']}.{version_parts['minor']}.{version_parts['patch']}"
build = version_parts['build']
if stage == 'dev':
    prerelease = 'alpha'
elif stage == 'qa':
    prerelease = 'beta'
elif stage == 'staging':
    prerelease = 'rc'
else:
    prerelease = ''

try:
   semver.parse(version_number)
except ValueError:
   print(f"Error: la versión actual '{version_number}' no es válida según SemVer")
   sys.exit(1)

new_version = ''
if stage == 'dev':
    try:
        if '[major]' in last_commit_message:
            new_version = semver.bump_major(version_number)

        elif '[minor]' in last_commit_message:
            new_version = semver.bump_minor(version_number)

        elif '[patch]' in last_commit_message:
            new_version = semver.bump_patch(version_number)

        else:
            print("Esta version no se incrementa")

    except ValueError:
       print("Error: acción de incremento inválida", ValueError)
       sys.exit(1)

new_version_number = semver.parse_version_info(version_number) if new_version == '' else semver.parse_version_info(new_version)
new_version_format = semver.format_version(
   major=new_version_number.major,
   minor=new_version_number.minor,
   patch=new_version_number.patch,
   prerelease=prerelease,
   build=CI_PIPELINE_ID
)

formatted_version = semver.format_version(
   major=new_version_number.major,
   minor=new_version_number.minor,
   patch=new_version_number.patch,
   build=CI_PIPELINE_ID
)


if stage == 'dev':
    if type == 'datapower':
        data['version'] = formatted_version
        with open(pathVersion, 'w') as file:
            json.dump(data, file, indent=2)
    else:
        current_version.text = formatted_version
        tree.write(pathVersion, pretty_print=True, xml_declaration=True, encoding="UTF-8")


    print(f'Nueva versión: {formatted_version}')

    tag_name = formatted_version
    commit_id = last_commit.hexsha
    tag_message = 'Esta es la version {}'.format(formatted_version)

    if version_number in repo.tags:
        repo.delete_tag(version_number)

    repo.create_tag(tag_name, ref=commit_id, message=tag_message, force=True)
    repo.create_tag(version_number, ref=commit_id, message=tag_message)

    remote.push(tag_name)
    remote.push(version_number)

    build_and_render(
        repository=".",
        output="CHANGELOG.md",
        convention="angular",
        template="keepachangelog",
        parse_trailers=True,
        parse_refs=False,
        sections=("build", "deps", "feat", "fix", "refactor", "ci", "docs", "perf", "revert"),
        bump_latest=True,
        in_place=True,
    )

    repo.git.add('--all')
    commit_message = 'ci: Version updated to {} [skip ci]'.format(new_version_format)
    repo.index.commit(commit_message)
    subprocess.run(["git", "push", "{}".format(PRIVATE_ACCESS_REPO), "HEAD:{}".format(REPO_BRANCH_NAME)])

print(f'Nueva versión sin prerelease: {formatted_version}')
print(f'Nueva versión: {new_version_format}')

buildTarget= new_version_format.replace("+","-")
with open('build.env', 'a') as file:
    file.write("BUILD_VERSION={}".format(buildTarget))
