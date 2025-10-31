## Configuration of OpenResty for FORC in a de.NBI Cloud setting with OpenID-Connect

### OpenResty + OIDC Plugin Installation

This guide describes the installation process on Ubuntu 18.04.

* Install OpenResty like it is described [here](https://openresty.org/en/linux-packages.html).
* Afterwards install the openidc plugin with `opm install zmartzone/lua-resty-openidc`.

### OpenResty configuration file

`/etc/openresty/nginx.conf` is the main configuration file for OpenResty. Consider this config template:

```
worker_processes  1;

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
                redirect_uri = "https://SERVERURL/redirect_uri",
                discovery = "https://login.elixir-czech.org/oidc/.well-known/openid-configuration",
                client_id = "YOUR ELIXIR CLIENTID",
                client_secret = "YOUR ELIXIR OIDC CLIENT SECRET",
                logout_path = "/logout",
                ssl_verify = "no"
          }
     }

    server {
        listen 80 default_server;
        server_name reverseproxy.bibiserv.projects.bi.denbi.de;
        return 301 https://$host$request_uri;
    }


    server {
        listen       443 ssl default_server;
        server_name  reverseproxy.bibiserv.projects.bi.denbi.de;
        ssl_certificate /etc/letsencrypt/live/reverseproxy.bibiserv.projects.bi.denbi.de/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/reverseproxy.bibiserv.projects.bi.denbi.de/privkey.pem;
        set $session_secret YOUR_SESSION_SECRET;

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
        include backends/*.conf;
        include /home/ubuntu/forc_config/backends/*.conf;

   error_page   500 502 503 504  /50x.html;
        location = /50x.html {
            root   html;
        }
    }
}
```

The important settings are here the OpenIDC credentials which is described in `init_by_lua_block`. Add here the credentials
of your OpenIDC-Client. Also make sure that you a have a matching redirect_url defined both in the OpenIDC-Client and the NGINX config.

In the `server` section please generate a strong `$session_secret`. Also provide your ssl keys and certificate in this group. You can also remove SSL from
this configuration and run OpenResty behind HAProxy with SSL-Termination.

In the last section of the config file, declare an `include` which points to the same directory registered in FORC as the backend path (`$FORC_BACKEND_PATH`).

