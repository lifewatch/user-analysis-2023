#! /usr/bin/env bash

docker exec -it lwua_jupyter jupyter server list | \
grep -P ^http | \
sed  's|//[^/]*/|//localhost:8888/|'| \
sed  's| :: .*||'