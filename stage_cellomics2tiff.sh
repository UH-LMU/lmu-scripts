#!/bin/bash
PROG=/nfs/hajaalin/Software/lmu-scripts/stage_cellomics2tiff.py
LOG=/home/hajaalin/staging/log/stage_cellomics2tiff_`date +%Y%m%d%H%M`.log

$PROG >& $LOG

