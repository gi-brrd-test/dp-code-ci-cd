pathEnvironment="environment/${ENVIRONMENT_}.json";
file_config="config.json";

config=$(base64 -w 0 "$file_config");
directorio_js="local";

data="{\"config\":\"$config\",\"domain\":\"$DOMAIN\",\"nameFolderDP\":\"$CI_PROJECT_TITLE\"";

if [ -d "$directorio_js" ]; then
  if [ "$(ls -A $directorio_js)" ]; then
      json="[";
      for archivo in "$directorio_js"/*; do
          if [ -f "$archivo" ]; then
              nombre_archivo=$(basename "$archivo")
              contenido_base64=$(base64 -w 0 "$archivo")
              json+='{"name": "'$nombre_archivo'", "content": "'$contenido_base64'"},'
          fi
      done
      json=$(echo "$json" | sed 's/,$//');
      json+="]"
     data+=",\"files\":$json";
  fi
fi
  if [ -f "$pathEnvironment" ]; then
  environment=$(base64 -w 0 "$pathEnvironment");
  data+=",\"environment\":\"$environment\"";
  fi
data+="}";
echo $data
