#!/bin/bash

activeroot=/mnt/lmu-active-rw
archiveroot=/mnt/lmu-archive-rw

# test data
active0=$activeroot/LMU-active2/archival-test
archive0=$archiveroot/LMU-archive2/archival-test

# LMU-active1 and LMU-active2
active1=$activeroot/LMU-active1/users
archive1=$archiveroot/LMU-archive1/users
active2=$activeroot/LMU-active2/users
archive2=$archiveroot/LMU-archive2/users

timestamp=`date +%Y%m%d%H%M`

condition="-mtime +365"
condition="-mtime -365"

# archive a user folder
archive_user() {
    from="$1"
    to="$2"
    user="$3"
    logdir="$4"
    echo $from $to/$user

    # list of file that will be transferred
    transferlist="$from/lmu-archive_${timestamp}_$user.txt"

    # log file
    transferlog="$logdir/lmu-archive_${timestamp}_$user.log"

    # find files to be transferred
    cd "$from"
    find . -type f $condition > "$transferlist"

    # transfer based on the list
    rsync -rv --files-from="$transferlist" . "$to/$user" >& "$transferlog"
}


# find user folders, archive one by one
archive() {
    from=$1
    to=$2
    logdir=$3
    mkdir -p "$logdir"

    # http://stackoverflow.com/questions/301039/how-can-i-escape-white-space-in-a-bash-loop-list
    while IFS= read -r -d '' userdir; do
	user=`basename "$userdir"`
	archive_user "$userdir" "$to" "$user" "$logdir"
    done < <(find $from -mindepth 1 -maxdepth 1 -type d -print0)
}

archive $active0 $archive0 $archive0/log
#archive $active1 $archive1 $archive1/log
#archive $active2 $archive2 $archive2/log
