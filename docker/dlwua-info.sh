#! /usr/bin/env bash

for dn in $(docker ps --format {{.Names}} | grep lwua_); do
  echo -e ">> $dn >>\n"
  docker inspect $dn | grep com.docker.compose.project
done 