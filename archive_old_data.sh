#!/bin/bash

usage() {
echo "$0 [options] input_dir archive_dir"
echo "Options:"
echo "-n dry run"
echo "-d delete from input_dir"
echo "-l /LMU-active2/users split logs to subfolders"
exit 1
}

while getopts ":ndl:" opt; do
case $opt in
n)
OPT_DRY_RUN=1
;;
d)
OPT_REMOVE_SOURCE_FILES=1
;;
l)
echo "-l was triggered, Parameter: $OPTARG" >&2
OPT_LOG_SPLIT_ROOT=$OPTARG
;;
\?)
echo "Invalid option: -$OPTARG" >&2
exit 1
;;
:)
echo "Option -$OPTARG requires an argument." >&2
exit 1
;;
esac
done
shift $((OPTIND-1))

# strip trailing slashes from directory names
active=`echo $1 | sed 's#/$##'`
archive=`echo $2 | sed 's#/$##'`

# check inputs
if [ ! -d "$active" ]; then
	echo "$active" is not a directory.
	exit
fi

if [ ! -d "$archive" ]; then
	echo "$archive" is not a directory.
	exit
fi

if [ ! -w "$active" ]; then
	echo "$active" is not writable.
	exit
fi

if [ ! -w "$archive" ]; then
	echo "$archive" is not writable.
	exit
fi



timestamp=`date +%Y%m%d%H%M`
timestamp=`date +%Y%m%d`
transferlist="$active"/transfer_`basename "$active"`_"$timestamp".txt
logfile="$active"/archive_`basename "$active"`_"$timestamp".log
echo transferlist: "$transferlist"
echo logfile: "$logfile"

# find files that are older than a year
#find "$active" -type f -mtime +365 > "$transferlist"

# edit file list so that paths start in the directory to be archived
sed -i "s#^.*$active##" "$transferlist"

# rsync files to archive
cmd="rsync -rv --files-from=$transferlist"
if [ -n "$OPT_DRY_RUN" ]; then
	cmd="$cmd --dry-run"
fi
if [ -n "$OPT_REMOVE_SOURCE_FILES" ]; then
	cmd="$cmd --remove-source-files"
fi
cmd="$cmd $active $archive >& $logfile"
echo "$cmd"
"$cmd"
