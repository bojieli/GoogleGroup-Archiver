#!/bin/bash
# This file should be run in crontab with sufficient permissions

BASEDIR=$(dirname "$0")
TMPDIR="$BASEDIR/tmp"
LOGFILE="$BASEDIR/archiver.log"

# list names of your mailing lists here, separated by comma
LISTS="ustc_lug lug shlug"

# your google group subscriber
EMAIL=example@gmail.com
PASSWORD=

python $BASEDIR/getnew.py $EMAIL $PASSWORD $LISTS >> $LOGFILE 2>&1

# update HTML
mkdir -p $TMPDIR
for l in $LISTS; do
    /usr/lib/mailman/bin/arch $l $TMPDIR/$l-delta.mbox >> $LOGFILE 2>&1
done
