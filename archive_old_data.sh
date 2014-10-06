#!/bin/bash

usage() {
echo "$0 [options] input_dir archive_dir"
echo "Options:"
echo "-n 			dry run"
echo "-d 			delete from input_dir"
echo "-l /LMU-active2/users 	split logs to subfolders"
echo "-t 200140903 		timestamp"
exit 1
}

while getopts ":ndl:t:" opt; do
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
t)
echo "-t was triggered, Parameter: $OPTARG" >&2
OPT_TIMESTAMP=$OPTARG
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

transferlist="$active"/transfer_`basename "$active"`_"$timestamp".txt
logfile="$active"/archive_`basename "$active"`_"$timestamp".log
echo 
echo transferlist: "$transferlist"
echo logfile: "$logfile"
echo

# find files that are older than a year
#find "$active" -type f -mtime +365 > "$transferlist"
find "$active" -type f -mtime -365 > "$transferlist"

# edit file list so that paths start in the directory to be archived
sed -i "s#^.*$active##" "$transferlist"

# rsync files to archive
rsync=`which rsync`
cmd="$rsync -rv --files-from=$transferlist"
if [ -n "$OPT_DRY_RUN" ]; then
	cmd="$cmd --dry-run"
fi
if [ -n "$OPT_REMOVE_SOURCE_FILES" ]; then
	echo using cmd="$cmd --remove-source-files"
fi
cmd="$cmd $active $archive"
echo rsync command: "$cmd >& $logfile"
echo
eval $cmd >& $logfile


split_logs() {
	logfile=$1
	inputdir=$2/$3
	inputsubdir=$3
	echo
	echo split_logs: $logfile $inputdir $inputsubdir

	# http://stackoverflow.com/questions/301039/how-can-i-escape-white-space-in-a-bash-loop-list
	while IFS= read -r -d '' subdir; do
		# use subdirectory name for log file naming
		base=`basename "$subdir"`
		sublog=$subdir/`basename $logfile .log`_$base.log

		# we want to grep from the start of the line,
		# so if logs are split for in a named subdirectory,
		# add the input subdirectory name to the search string
		if [ -n $inputsubdir ]; then
			base=$inputsubdir/$base
		fi

		echo "grep ^$base $logfile >& $sublog"
		if [ -z "$OPT_DRY_RUN" ]; then
			grep "^$base" "$logfile" >& "$sublog"
		fi

    	done < <(find $inputdir -mindepth 1 -maxdepth 1 -type d -print0)
}


# split log file per subdirectories of the input folder
split_logs $logfile $active

# split log file per subsubdirectories of the input folder
if [ -n $opt_LOG_SPLIT_ROOT ]; then
	split_logs $logfile $active $OPT_LOG_SPLIT_ROOT
fi

