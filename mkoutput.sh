#! /bin/bash

if [ $# -ne 1 ]; then
  echo "usage: `basename $0` filename num" 1>&2
  exit 1
fi

input=$1
num_file=`ls ./output | wc -l`
let num=`expr ${num_file}+1`
echo ${num}
cat ${input} | tr -d "\n" | sed -e "s/  */ /g"  > ./output/output${num}.txt

echo "Done ..."
