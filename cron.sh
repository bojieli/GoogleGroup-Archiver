#!/bin/bash
# This file should be run in crontab with sufficient permissions

if [ ! -d "$1" ]; then
    echo "The first param should be ABSOLUTE PATH to this project"
    exit 1
fi
BASEDIR=$1
TMPDIR="/tmp"
LOGFILE="/var/log/lugmailbox.log"

# list names of your mailing lists here, separated by comma
LISTS="ustc_lug lug shlug"

# your google group subscriber
EMAIL=example@gmail.com
PASSWORD=

python $BASEDIR/getnew.py $EMAIL $PASSWORD $LISTS >> $LOGFILE 2>&1

# update HTML
for l in $LISTS; do
    /usr/lib/mailman/bin/arch $l $TMPDIR/$l-delta.mbox >> $LOGFILE 2>&1
done
