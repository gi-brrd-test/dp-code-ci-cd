pathEnvironment="environment/${ENVIRONMENT_}_parameters.json"

file_config="config.json";
config=$(base64 -w 0 "$file_config");
directorio_js="local";

data="{\"config\":\"$config\",\"domain\":\"$DOMAIN\",\"nameFolderDP\":\"$GRUPO_FUNCIONAL\"";

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

# styleParameters opcional
if [ -f "$pathEnvironment" ]; then
  styleParameters=$(jq -c '.styleParameters // empty' "$pathEnvironment")
  if [ -n "$styleParameters" ]; then
    data+=",\"styleParameters\":$styleParameters"
  fi
fi

data+="}";
echo $data