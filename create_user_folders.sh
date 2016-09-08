#!/bin/bash

active=("/mnt/lmu-active/LMU-active1/users" "/mnt/lmu-active/LMU-active2/users" "/mnt/lmu-active/LMU-active3/users")
archive=("/mnt/lmu-archive/LMU-archive1/users" "/mnt/lmu-archive/LMU-archive2/users" "/mnt/lmu-archive/LMU-archive3/users")
netapp=("/mnt/lmu-netapp/users")
mednas=("/mnt/med-groups/lmu/ls1/users" "/mnt/med-groups/lmu/ls2/users" "/mnt/med-groups/lmu/lmu_archive/users")

bases=("${active[@]}" "${archive[@]}" "${netapp[@]}" "${mednas[@]}")
#bases=("/home/hajaalin/netapp/lmu/users" "/mnt/lmu-active/LMU-active1/users" "/mnt/lmu-active/LMU-active2/users" "/mnt/lmu-active/LMU-active3/users" "/mnt/lmu-archive/LMU-archive1/users" "/mnt/lmu-archive/LMU-archive2/users" "/mnt/lmu-archive/LMU-archive3/users")

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
