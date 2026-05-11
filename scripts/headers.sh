#!/bin/sh

headers=(
  "Content-Type: application/json"
  "_user: $1"
  "_pass: $2"
  "_ip_dp: $3"
  "_environment: $4"
)

for header in "${headers[@]}"; do
  header_args+=("--header" "'$header'")
done

echo "${header_args[@]}"