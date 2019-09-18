#!/bin/bash
#configure /etc/yum.repos.d/CentOS-Base.repo
#params: 1.host 2.centos version, 6 or 7
host=$1
v=$2
if [ -z "${host}" ]; then
  echo "Host is null"
else
  if [[ ${v} -eq 6 || ${v} -eq 7 ]]; then
    cat resources/yum-base-template.repo | sed 's/{host}/'${host}'/g' | sed 's/{v}/'${v}'/g'
    cat resources/yum-base-template.repo | sed 's/{host}/'${host}'/g' | sed 's/{v}/'${v}'/g' >/etc/yum.repos.d/CentOS-Base.repo
  else
    echo "Incorrect version: ${v}"
  fi
fi
