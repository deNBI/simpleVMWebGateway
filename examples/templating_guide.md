# FORC Templating

### Overview

FORC uses so called templates in order to generate multiple backends, which are just nginx config snippets defining URL locations.

These Templates include [jinja2](https://jinja.palletsprojects.com/en/2.10.x/) fields in the form of `{{ variable }}`.
By setting some fields in a template, we can generate backend config files in various forms.

Templates are located in the path you defined with the environment variable `FORC_TEMPLATE_PATH`.
A Template filename needs to be named in a specific way.

Templates contain the **name** of the template itself, and a **version number**. Name and version are seperated with a `%` sign.
Also, template filenames need to end with `.conf`.

These are valid template filenames:

* `rstudio%v01.conf`
* `jupyter%1337.conf`
* `guac%version17.conf`

By placing them inside `FORC_TEMPLATE_PATH`, they are directly ready to use by FORC without reloadin the service.

### Example Template

This is an example Template for the research environment [RStudio](https://rstudio.com).

```
    location /{{ key_url }}/ {
            # Run this lua block, which checks if we are authenticated (again) und filters request by JWT (via id_token.sub)
            access_by_lua_block {
                    -- Start actual openid authentication procedure
                    local res, err = require("resty.openidc").authenticate(opts2)
                    -- If it fails for some reason, escape via HTTP 500
                    if err then
                            ngx.status = 500
                            ngx.say(err)
                            ngx.exit(ngx.HTTP_INTERNAL_SERVER_ERROR)
                    end

                    -- Protect this location and allow only one specific ELIXIR User
                    if res.id_token.sub ~= "{{ owner }}@elixir-europe.org" then
                            ngx.exit(ngx.HTTP_FORBIDDEN)
                    end
            }


      rewrite ^/{{ key_url }}/(.*)$ /$1 break;
      proxy_pass {{ location_url }};
      proxy_redirect {{ location_url }} $scheme://$http_host/rstudio/;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection $connection_upgrade;
      proxy_read_timeout 20d;
}
```