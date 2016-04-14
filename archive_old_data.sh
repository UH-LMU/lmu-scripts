#!/bin/bash

usage() {
echo "$0 [options] input_dir archive_dir"
echo "Options:"
echo "-n 			dry run"
echo "-d 			delete from input_dir"
echo "-m 365 	mtime, move files older than this"
echo "-t 200140903 		timestamp"
echo "-l LMU-active1 		label"
exit 1
}

while getopts ":ndt:m:l:" opt; do
case $opt in
n)
OPT_DRY_RUN=1
;;
d)
OPT_REMOVE_SOURCE_FILES=1
;;
t)
echo "-t was triggered, Parameter: $OPTARG" >&2
OPT_TIMESTAMP=$OPTARG
;;
m)
echo "-m was triggered, Parameter: $OPTARG" >&2
OPT_MTIME=$OPTARG
;;
l)
echo "-l was triggered, Parameter: $OPTARG" >&2
OPT_LABEL=$OPTARG
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
if [ -z $active ]; then
	usage
fi

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


timestamp=${OPT_TIMESTAMP:-`date +%Y%m%d%H%M`}
mtime=${OPT_MTIME:-"365"}
label=${OPT_LABEL:-`basename "$active"`}

transferlist="$active"/transfer_`basename "$active"`_"$timestamp".txt
logfile="$active"/archive_"$label"_"$timestamp".log
echo
echo transferlist: "$transferlist"
echo logfile: "$logfile"
echo

# find files that are older than a year
find "$active" -type f -daystart -mtime +${mtime} > "$transferlist"
#find "$active" -type f -mtime -365 > "$transferlist"

# edit file list so that paths start in the directory to be archived
sed -i "s#^.*$active##" "$transferlist"

# rsync files to archive
rsync=`which rsync`
cmd="$rsync -rv --files-from=$transferlist"
if [ -n "$OPT_DRY_RUN" ]; then
	cmd="$cmd --dry-run"
fi
if [ -n "$OPT_REMOVE_SOURCE_FILES" ]; then
	cmd="$cmd --remove-source-files"
fi
cmd="$cmd $active $archive"
echo rsync command: "$cmd >& $logfile"
echo
eval $cmd >& $logfile


split_log() {
	logfile=$1
	inputdir=$2
	echo
	echo split_log: $logfile $inputdir

	# http://stackoverflow.com/questions/301039/how-can-i-escape-white-space-in-a-bash-loop-list
	while IFS= read -r -d '' subdir; do
		# use subdirectory name for log file naming
		base=`basename "$subdir"`
		sublog=$subdir/`basename $logfile .log`_$base.log

		echo "grep ^$base/ $logfile >& $sublog"
		if [ -z "$OPT_DRY_RUN" ]; then
			grep "^$base/" "$logfile" >& "$sublog"
		fi

    	done < <(find $inputdir -mindepth 1 -maxdepth 1 -type d -print0)
}


# split log file per subdirectories of the input folder
split_log $logfile $active
