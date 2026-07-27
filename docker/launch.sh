#!/bin/bash

#/usr/local/openresty/nginx/sbin/nginx -g 'daemon on; master_process on;'
gunicorn -c gunicorn_conf.py main:app