#!/usr/bin/env bash
HTTPC_LIB="./httpc"

echo "##### GET a list of files in working directory #####"
${HTTPC_LIB} get -v "http://localhost:8080/"

echo ""

echo "##### GET the content of the index.html file #####"
${HTTPC_LIB} get -v "http://localhost:8080/index.html"

echo ""

echo "##### POST to test.json #####"
${HTTPC_LIB} post -v "http://localhost:8080/test.json" -h Content-Type:application/json -d "{'Assignment':1}"

echo ""

echo "##### POST to test_date.json (create file) #####"
DATE=$(date +'%Y_%m_%d_%H_%M_%S')
${HTTPC_LIB} post -v "http://localhost:8080/test_${DATE}.json" -h Content-Type:application/json -d "{'Assignment':1}"

echo ""

echo "##### Test unrestricted access #####"
${HTTPC_LIB} get -v "http://localhost:8080/../../index.html"

echo ""

echo "##### Testing multiple requests - One will return 409 Conflict #####"
${HTTPC_LIB} get -v "http://localhost:8080/sample.sql" &
${HTTPC_LIB} get -v "http://localhost:8080/sample.sql" &

#${HTTPC_LIB} post -v "http://localhost:8080/python.html" -h Content-Type:text/html -f ../working_dir/python.html &
