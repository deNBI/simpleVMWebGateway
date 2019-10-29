## FORC+OpenResty in Docker

### Guide

This folder contains the setup for FORC+OpenResty in Docker.

In order to run this container, you need to provide it with a ready configured `nginx.conf` file.

A minimal file could look this:

````
worker_processes  10;
# /usr/local/openresty/nginx/logs/
error_log  logs/error.log;
error_log  logs/error.log  notice;
error_log  logs/error.log  info;
error_log  logs/error.log  debug;
events {
    worker_connections  1024;
}
http {
    include       mime.types;
    default_type  application/octet-stream;
    #For some reason, nginx wants a hardcoded Name Resolver
    resolver 8.8.8.8;
    sendfile        on;
    keepalive_timeout  65;
    #LUA caches for various session modules
    lua_shared_dict discovery 1m;
    lua_shared_dict jwks 1m;
    lua_code_cache off;

     #Allow websockets by allowing general connection upgrade requests, theia needs websockets
     map $http_upgrade $connection_upgrade {
         default upgrade;
        '' close;
       }

    #Create global LUA variable which keeps our ELIXIR AAI Configuration dict
    init_by_lua_block {
         opts2 = {
                redirect_uri = "http://reverseproxy.bibiserv.projects.bi.denbi.de/redirect_uri",
                discovery = "https://login.elixir-czech.org/oidc/.well-known/openid-configuration",
                client_id = "CLIENTID",
                client_secret = "CLIENTSECRET",
                logout_path = "/logout",
                ssl_verify = "no"
          }
     }


 server {
        listen 5000;
        location / {
                include uwsgi_params;
                uwsgi_pass unix:/var/run/forc.sock;
                }
        }

server {
        listen 0.0.0.0:80;
        server_name  reverseproxy.bibiserv.projects.bi.denbi.de;
        set $session_secret fdhtzzu45z34t32g24f43;

        location / {

                access_by_lua_block {
                -- Start actual openid authentication procedure
                local res, err = require("resty.openidc").authenticate(opts2)
                -- If it fails for some reason, escape via HTTP 500
                if err then
                        ngx.status = 500
                        ngx.say(err)
                        ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
                end

        }

        }

        #Load all dynamicaly created locations.
        include /var/forc/backend_path//*.conf;

       error_page   500 502 503 504  /50x.html;
            location = /50x.html {
                root   html;
            }
    }
}

````

In this config file, adjust your oidc-client credentials in the `opts2` field and make changes to `servername`.

This container pushes port `80` for reverse-proxied webcontent and port `5000` for the forc api.

Generate a strong API Key for forc.

Summing up, you can then build the container and run it afterwards:

````
docker build -t forc .

docker run -p 5656:5000 -p 5657:80 -v nginx.conf:/etc/openresty/nginx.conf -e "FORC_API_KEY=somerandompw"  forc
````

Path for forc backends and templates are the default ones:

````
/var/forc/backend_path/
/var/forc/template_path/
````

For convenience, it is recommended to mount these folders as a volume to the container.
