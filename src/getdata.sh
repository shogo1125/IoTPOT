#! /bin/bash

set -e
 . /opt/telnet_hoeny/etc/config.sh
set +e

function usage(){
  if [ $# -ne 2 ]; then
    echo "usage: `basename $0` filename num" 1>&2
    exit 1
  fi
}

function check_datafile_existance(){
  if [ ! -e "${DATAFILE}" ]; then
    echo "file "${DATAFILE}" not found"
    exit 1
  fi
}

usage
check_datafile_existance
OPTION=`sed -n "$1"p "${DATAFILE}" | cut -d "," -f "$2"`
echo -ne "${OPTION}"
