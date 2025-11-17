#!/usr/bin/execlineb -P
with-contenv
/bin/export HOME /data/rtorrent
/bin/export PWD /data/rtorrent
s6-setuidgid 1000:1000
rtorrent -D -o import=/etc/rtorrent/.rtlocal.rc -o import=/data/rtorrent.rc

