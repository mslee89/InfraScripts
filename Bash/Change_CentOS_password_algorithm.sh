#!/bin/sh

RESULT=`authconfig --test | grep algorithm | awk '{print $5}'`

if [ RESULT == 'md5' ]; then
    authconfig --passalgo=sha512 --update
    AFTER_RESULT=`authconfig --test | grep algorithm | awk '{print $5}'`
    echo `hostname` : "Done -" $RESULT "-->" $AFTER_RESULT
    exit 0
elif [ RESULT == 'sha512' ]; then
    echo `hostname` : "You don not need change to algorithm on this server -" $RESULT
    exit 0
else
    echo `hostname` : "Failed"
    exit 0
fi