#!/usr/bin/env bash
HTTPC_LIB="./httpc"

${HTTPC_LIB} get -v "http://localhost:8080/sample.sql" &
${HTTPC_LIB} get -v "http://localhost:8080/sample.sql" &
#${HTTPC_LIB} post -v "http://localhost:8080/index.json" -h Content-Type:application/json -d '{"Assignment": 1}'
