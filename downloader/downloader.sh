#!/bin/sh

set -e 
. ../etc/config.sh
set +e

HASH_MALWARE="hash_malware"
HASH_TMP="hash_tmp"
COMMANDS="../wget-command"
BINARY="new_malware"

wget_malware(){
  cd ./tmp
  while read command 
  do
    `${command}`
    if [ $? -ne 0 ]; then
      echo "`date +%Y-%m-%d %H:%M:%S`:${command}" >> ../log/get-to-fail
    fi
  done<${COMMANDS} 
  md5sum ./* > ../${HASH_TMP}
  cd ../
  echo "download done ..."
}

check_file(){
  grep -Fwv -f ${HASH_MALWARE} ${HASH_TMP} > ./hash
  CHECK=`wc -l ./hash | cut -d " " -f 1`
  DIR_NAME=`date +%Y%m%d`
  echo "${DIR_NAME}:new-file:${CHECK}" >> ./log/status
  if [ ${CHECK} -eq 0 ]; then 
    echo "NO NEW MALWARE"
  else
    mkdir -p ${BINARY}/${DIR_NAME} 
    FILE_NAME=`cat ./hash| cut -d "/" -f 2`
    #echo "debug filename:${FILE_NAME}"
    for file in ${FILE_NAME}
    do 
      echo "${DIR_NAME}:${file}" >> ./log/malware/${file}.log
      mv ./tmp/${file} ./${BINARY}/${DIR_NAME}
    done
    file ./${BINARY}/${DIR_NAME}/* | cut -d "/" -f 4- | mailx -s ": DOWNROADER INFO [$(date +%F)]" ${MAIL_ADDRESS} 
    cat ./hash | cut -d " " -f 1 >> ${HASH_MALWARE}
    chmod 000 ./${BINARY}/${DIR_NAME}/*
  fi
  echo "file check done ..."
}

rm_files(){
  rm ./hash_tmp
  rm ./hash
  rm ./tmp/*
}

wget_malware
check_file
rm_files
