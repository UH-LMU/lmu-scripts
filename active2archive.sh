#!/bin/bash

activeroot=/input
archiveroot=/output

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
    echo $from $to

    logdir=$to/log
    mkdir -p "$logdir"
    user=`basename "$from"`
    transferlog="$logdir/lmu-archive_${timestamp}_$user.log"

    transferlist="$from/lmu-archive_$timestamp.txt"
    find "$from" -type f $condition > "$transferlist"
    cmd="rsync -rvn --files-from=\"$transferlist\" \"$from\" \"$to\" >& \"$transferlog\""
    echo $cmd
    $cmd
}


# find user folders, archive one by one
archive() {
    from=$1
    to=$2
    # http://stackoverflow.com/questions/301039/how-can-i-escape-white-space-in-a-bash-loop-list
    while IFS= read -r -d '' n; do
	archive_user "$n" "$to"
    done < <(find $from -mindepth 1 -maxdepth 1 -type d -print0)
}

archive $active0 $archive0 
#archive $active1 $archive1
#archive $active2 $archive2
