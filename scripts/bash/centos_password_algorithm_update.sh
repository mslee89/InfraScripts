#!/bin/sh
# CentOS 6 이하에서 알고리즘을 변경하는 스크립트

RESULT=$(authconfig --test | grep algorithm | awk '{print $5}')

if [ "$RESULT" = "md5" ]; then
    authconfig --passalgo=sha512 --update
    AFTER_RESULT=$(authconfig --test | grep algorithm | awk '{print $5}')
    echo "$(hostname): Password algorithm updated - $RESULT → $AFTER_RESULT"
elif [ "$RESULT" = "sha512" ]; then
    echo "$(hostname): No change needed - Current algorithm is $RESULT"
else
    echo "$(hostname): Failed to detect password algorithm"
    exit 2
fi