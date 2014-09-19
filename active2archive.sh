#!/bin/bash

activeroot=/input
archiveroot=/output

active1=$activeroot/LMU-active1/users
active2=$activeroot/LMU-active2/users
archive1=$archiveroot/LMU-archive1/users
archive2=$archiveroot/LMU-archive2/users

archive_user() {
    from=$1
    to=$2
    echo $from $to
}


archive() {
    from=$1
    to=$2
    # http://stackoverflow.com/questions/301039/how-can-i-escape-white-space-in-a-bash-loop-list
    while IFS= read -r -d '' n; do
	#printf '%q\n' "$n"
	archive_user "$n" "$to"
    done < <(find $from -maxdepth 1 -type d -print0)
}

archive $active1 $archive1
archive $active2 $archive2
