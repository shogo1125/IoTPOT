#! /bin/bash

if [ $# -ne 2 ]; then
  echo "usage: `basename $0` filename num" 1>&2
  exit 1
fi

datafile=./datafile
if [ ! -e "${datafile}" ]; then
  echo "file "${datafile}" not found"
  exit 1
fi

output=`sed -n "$1"p "${datafile}" | cut -d "," -f "$2" `
echo -ne "${output}"
