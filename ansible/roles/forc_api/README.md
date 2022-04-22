Role Name
=========

This role installs the [FastapiOpenRestyConfigurator](https://github.com/deNBI/simpleVMWebGateway) and optionally OpenResty
with all needed plugins and SSL certs.

Requirements
------------

Needed requirements:

* Ubuntu 18.04 Bionic
* Access to instance via standard ports (80, 443)
* DNS Name for autogenerating ssl certs via certbot.
* OpenID Connect client.


Role Variables
--------------

**vars/main.yml**

| Variable                  | Description           | Default                                                                       | Mandatory |
| -------------             |-------------          |            -----                                                              |     ---   |
| FORC_SECRET_KEY           | Encryption key for flask service |                                                                    | Yes       |
| FORC_API_KEY              | X-Auth Key for accessing REST API                                     |                               | Yes       |
| FORC_BACKEND_PATH         | Filesystem path in where FORC generates NGINX config snippets to      |    /var/forc/backend_path/    |   Yes     |
| FORC_TEMPLATE_PATH        | Filesystem path which locates template files for FORC                 | /var/forc/template_path/      | Yes       |
| FORC_SERVICE_PORT         | The Port on which OpenResty will bind forc to.                        | 5000                          | Yes       |
| FORC_OIDC_DISCOVERY_URL   | OIDC Credentials                                                      | https://login.elixir-czech.org/oidc/.well-known/openid-configuration  | Yes |
| FORC_OIDC_CLIENT_ID       | OIDC Credentials                                                      |                               | Yes       |
| FORC_OIDC_CLIENT_SECRET   | OIDC Credentials                                                      |                               | Yes       |
| DOMAIN                    | The domain name of the webserver serving forc and OpenResty           |                               | Yes       |
| CERTBOT_USED              | Set this to no if you don't use certbot for autogenerating ssl certs. | yes                           | No        |
| INSTALL_OPENRESTY         | Set this to no if you only want to install forc as uWSGI app.         | yes                           | No        |
| FORC_BACKUP_ENABLED       | If Backups from backends and templates folder will be created         | yes                           | NO        |
| FORC_BACKUP_HOST_PATH     | Where the Backups will be stored on the host                          | /persistent/backup/forc       | No        |
| FORC_BACKUP_ROTATION_ENABLED | If the Backups will be rotated                                     | true                          | No        |
| FORC_BACKUP_ROTATION_MAX_SIZE | When this size of the backups folder is reached the backups are rotated | 5                       | No        |
| FORC_BACKUP_ROTATION_CUT_SIZE | Deletes oldest Backups till this  size is reached                 | 4                             | No        |
| FORC_BACKUP_ROTATION_SIZE_TYP| Size Type For Rotation                                             | GiB                           | No        |


**defaults/main.yml**

| Variable                  | Description           | Default                     | Mandatory |
| -------------             |-------------          |            -----           |     ---   |
| OPENRESTY_WORKER_PROCESSES | Number of worker processes for the OpenResty webserver. | 10 | Yes |
| OPENRESTY_DNS_SERVERS     | Resolver needed by OpenResty  | 8.8.8.8   | Yes |
| FORC_INSTALLATION_PATH    | Path on where forc will be installed to | /opt/   | Yes |



Dependencies
------------

If auto generating certs is wanted:

* geerlingguy.certbot 

A requirements.yml is placed in the ansible folder. If you have question on how a requirements.yml is used, please visit [here](https://galaxy.ansible.com/docs/using/installing.html#installing-multiple-roles-from-a-file).

Example Playbook
----------------

To install OpenResty+certbot(+renewal)+FORC:

    - hosts: all
      become: yes
      vars:
        domain: reverseproxy.bibiserv.projects.bi.denbi.de

      roles:
        - role: geerlingguy.certbot
          certbot_admin_email: mail@mail.de
          certbot_create_if_missing: true
          certbot_create_standalone_stop_services: []
          certbot_auto_renew_user: root
          certbot_auto_renew_options: "--pre-hook "systemctl stop openresty" --post-hook "systemctl start openresty" --quiet --no-self-upgrade"

          certbot_certs:
          - domains:
            - "{{ domain }}"

        - role: forc_api
          FORC_SECRET_KEY: fdhtzzu45z34t32g24f43
          FORC_API_KEY: vcnufez3jf39wvfngv0
          FORC_OIDC_CLIENT_ID: fsduiofgjwepogjerohigjeroigjer
          FORC_OIDC_CLIENT_SECRET: fmsdgndsogijwsgjtdfogjreowigj
          DOMAIN: "{{ domain }}"

License
-------

Apache 2.0

Author Information
------------------

Alex Walender

de.NBI Cloud Bielefeld
