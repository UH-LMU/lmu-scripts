#!/bin/bash

ACT="/mnt/lmu-active"
ACT_RW="/mnt/lmu-active-rw"
ARCH="/mnt/lmu-archive"
ARCH_RW="/mnt/lmu-archive-rw"
B973="/mnt/FROM_BIOTEK973"

for disk in $ACT $ACT_RW $ARCH $ARCH_RW $B973
do
	ls $disk >& /dev/null
done

