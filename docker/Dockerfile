FROM ubuntu:22.04
MAINTAINER awalende


ENV FORC_BACKEND_PATH=/var/forc/backend_path/
ENV FORC_TEMPLATE_PATH=/var/forc/template_path/

RUN mkdir -p /var/forc/backend_path/; mkdir -p /var/forc/template_path/

RUN apt-get update; apt-get install -y sudo git wget gnupg ca-certificates software-properties-common python3 python3-pip python-setuptools; pip3 install uwsgi
RUN wget -O - https://openresty.org/package/pubkey.gpg | sudo apt-key add -
RUN add-apt-repository -y "deb http://openresty.org/package/ubuntu $(lsb_release -sc) main"
RUN apt-get update
RUN apt-get -y install openresty
RUN opm install zmartzone/lua-resty-openidc
RUN mkdir -p /opt/simpleVMWebGateway
RUN git clone https://github.com/deNBI/simpleVMWebGateway.git /opt/simpleVMWebGateway/
RUN pip3 install -r /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator/requirements.txt

WORKDIR /opt/simpleVMWebGateway/FastapiOpenRestyConfigurator

COPY uwsgi.ini uwsgi.ini
COPY launch.sh launch.sh
RUN chmod +x launch.sh

CMD ./launch.sh
