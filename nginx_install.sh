#!/bin/bash
#nginx install

yum install gcc gcc-c++ patch

nginx_path="/root/nginx"
openssl="openssl-1.0.2l"
zlib="zlib-1.2.11"
pcre="pcre-8.42"
nginx="nginx-1.12.2"

mkdir -p ${nginx_path}

tar -xvf resources/tar/openssl* -C ${nginx_path}
tar -xvf resources/tar/pcre* -C ${nginx_path}
tar -xvf resources/tar/zlib* -C ${nginx_path}
tar -xvf resources/tar/nginx* -C ${nginx_path}
unzip resources/tar/ngx_req_status.zip -d ${nginx_path}

cd ${nginx_path}/${zlib} && ./configure && make && make install
cd ${nginx_path}/${pcre} && ./configure && make && make install
cd ${nginx_path}/${openssl} && ./configure && make && make install

cd ${nginx_path}/${nginx}
patch -p1 <../ngx_req_status-master/write_filter-1.7.11.patch
./configure --prefix=/usr/local/nginx \
  --with-openssl=${nginx_path}/${openssl} \
  --with-pcre=${nginx_path}/${pcre} \
  --with-zlib=${nginx_path}/${zlib} \
  --with-http_ssl_module --with-http_stub_status_module \
  --add-module=${nginx_path}/ngx_req_status-master
make && make install
