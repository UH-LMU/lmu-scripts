#!/bin/bash

input=$1
output="$input".txt

gawk -f print_logons_and_logoffs.awk "$input" > "$output"


