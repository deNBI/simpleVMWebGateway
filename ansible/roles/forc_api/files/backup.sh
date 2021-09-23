#!/bin/sh

NOW=$(date '+%y-%m-%d-%H%M')

FILE=/etc/backup/backends-${NOW}.tar.gz
tar czvf $FILE /backends /templates
