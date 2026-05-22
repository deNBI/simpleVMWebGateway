#!/bin/bash

/usr/local/openresty/nginx/sbin/nginx -g 'daemon on; master_process on;'
uwsgi --ini uwsgi.ini