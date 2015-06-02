#! /bin/bash
set -e
  . /opt/iotpot/etc/config.sh
set +e

if [ $# -ne 2 ]; then
  echo "usage: `basename $0` filename num" 1>&2
  exit 1
fi

if [ ! -e "${LOGIN_PATH}" ]; then
  echo "file "${LOGIN_PATH}" not found"
  exit 1
fi

OUTPUT=`sed -n "$1"p "${LOGIN_PATH}" | cut -d "," -f "$2" `
echo -ne "${OUTPUT}"
