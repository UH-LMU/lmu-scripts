#!/bin/bash

bases=("/mnt/lmu-active/LMU-active1/users" "/mnt/lmu-active/LMU-active2/users" "/mnt/lmu-archive/LMU-archive1/users" "/mnt/lmu-archive/LMU-archive2/users")

users=$(ldapsearch -H ldaps://ldap-internal.it.helsinki.fi:636 -x -s sub -b ou=alma_workgroups,ou=groups,o=hy "(&(uid=grp-A91900-lmu-cust))" \
|grep uniqueMember|cut -d' ' -f2 |cut -d, -f1|cut -d'=' -f2|tr '[:upper:]' '[:lower:]'|sort)


for base in ${bases[@]}; do
  #echo $base

  for user in $users; do
    letter=$(echo $user | cut -c1)
    dir=${base}/${letter}/$user
    echo $dir
    mkdir -p $dir
  done

done
