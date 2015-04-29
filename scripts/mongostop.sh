#!/bin/sh

mongostop_func () {
  local mongopid=`less /opt/local/var/db/mongodb_data/mongod.lock`;
  if [[ $mongopid =~ [[:digit:]] ]]; then
      sudo kill -15 $mongopid;
      echo mongod process $mongopid terminated;
  else
      echo mongo process $mongopid not exist;
  fi
}

mongostop_func

