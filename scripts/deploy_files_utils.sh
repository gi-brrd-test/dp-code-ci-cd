#!/bin/bash

carpeta="$1"
domain="$2"

# Carpeta relativa sin "local/"
nameFolderDP="${carpeta#local/}"

json="{\"domain\":\"$domain\",\"nameFolderDP\":\"$nameFolderDP\",\"files\":["
for file in "$carpeta"/*.js; do
  nombre=$(basename "$file")
  contenido=$(base64 -w 0 "$file")
  json+="{\"name\":\"$nombre\",\"content\":\"$contenido\"},"
done
json="${json%,}]}"  # Quita coma final

# Output del JSON
echo "$json"
