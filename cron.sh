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

mkdir -p $TMPDIR
python $BASEDIR/getnew.py $EMAIL $PASSWORD $TMPDIR $LISTS >> $LOGFILE 2>&1

# update HTML
for l in $LISTS; do
    /usr/lib/mailman/bin/arch $l $TMPDIR/$l-delta.mbox >> $LOGFILE 2>&1
done
