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

This generates into a backend for OpenResty by creating a config snippet in the path defined in `FORC_BACKEND_PATH`.
FORC automatically reloads OpenResty after a change, so that those backends can be directly served to a user.

In order to generate a backend from a template, you need to pass the following jinja2 variables:

| Variable        | Description           | Example  |
| ------------- |:-------------:| -----:|
| key_url      | The name of the URL subpath in which the service should be accessable. | myFavoriteRstudio |
| owner         | Restrict access to service only to this ELIXIR AAI User (pass without @elixir mail prefix) | 	a9ffc9fb32e35f16d019a9acceeaa08e7ceehdue ||
| location_url | The path to the service you would like to serve via FORC reverse proxy. | http://192.168.17.3:5000 |


### Example API Call

We want to register a new backend for an ELIXIR User with the following data:

* The research environment should be accessable via `https://<reverse_proxy_url>/myRstudio`. FORC will actually add a unique ID as a suffix to avoid conflicts. The actual path would probably look like `/myRstudio_001/`.
* The owner has the ELIXIR ID `a9ffc9fb32e35f16d019a9acceeaa08e7ceehdue`. Again, don't pass in the rest of the ELIXIR ID (no @elixir-europe.org). Only this user is allowed to access the resource.
* The actual service is running at `http://192.168.17.3:5000`, we want to reverse proxy this location via FORC to the user.
* The targeted service is a RStudio instance.
* We want to use a specific version of the rstudio template: `v01`.

A `cURL` call will look like this:

`curl -X POST "https://reverseproxy.bibiserv.projects.bi.denbi.de:5000/backends/" -H "accept: application/json" -H "X-API-KEY: $API_KEY" -H "Content-Type: application/json" -d "{ \"owner\": \"a9ffc9fb32e35f16d019a9acceeaa08e7ceehdue\", \"user_key_url\": \"myRstudio\", \"upstream_url\": \"http://192.168.17.3:5000\", \"template\": \"rstudio\", \"template_version\": \"v01\"}"`

If everything is correct, FORC will return a JSON Object in return, specifying the final callable sub-url path. A response could look like this:

``` 
{
  "id": 3892998658,
  "owner": "a9ffc9fb32e35f16d019a9acceeaa08e7ceehdue",
  "location_url": "myRstudio_100",
  "template": "rstudio",
  "template_version": "v01"
}
```

In this example, the user can now access the resource via `https://reverseproxy.bibiserv.projects.bi.denbi.de/myRstudio_100/` by pointing
the browser to this URL. Before reaching the resource, the user needs to authenticate via ELIXIR AAI. 