#!/bin/bash

set -e

_blue() {
  echo -e "\e[1;36m$@\n\e[0m"
}
_red() {
  echo -e "\e[1;31m$@\e[0m"
}
_green() {
  echo -e "\e[1;32m$@\n\e[0m"
}
_yellow() {
  echo -e "\e[1;33m$@\e[0m"
}
_check_pck() {
  _yellow Checking $1
  if (( $(echo "$2 > $3" | bc -l ) ))
  then
    _green Pass;
  else
    _red $1 version $3 or higher is not installed. Install missing package. Refer to https://docs.docker.com/engine/install/binaries/#prerequisites
    exit
  fi
}

_check_root_user() {
  if [[ $EUID -ne 0 ]]
  then
    red "$0 is not running as root. Switch to root user before running script."
    exit
  else
    _green Pass
  fi
}

XZ_VERSION=$(xz --version  | grep -Eo '[0-9]\.[0-9]+' |  head -n 1 || echo 0.0)
GIT_VERSION=$(git --version | grep -Eo '[0-9]\.[0-9]+' || echo 0.0)
IPTABLES_VERSION=$(iptables --version | grep -Eo '[0-9]\.[0-9]+' || echo 0.0)

_blue Checking user is root

_check_root_user

_blue Checking prerequisites before installing docker binary.

_check_pck xz_utils $XZ_VERSION 4.9
_check_pck git $GIT_VERSION 1.7
_check_pck iptables $IPTABLES_VERSION 1.4

_blue Untarring docker and copying docker, docker-compose binary files to /usr/bin

tar xzvf ./docker-20.10.9.tgz
cp docker/* /usr/bin/
cp ./docker-compose /usr/bin/ && chmod +x /usr/bin/docker-compose

_blue Creating docker service files. Starting docker service.
# https://docs.docker.com/config/daemon/systemd/#manually-create-the-systemd-unit-files
cat << EOF > /etc/systemd/system/docker.service
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network-online.target docker.socket firewalld.service containerd.service time-set.target
Wants=network-online.target containerd.service
Requires=docker.socket

[Service]
Type=notify
# the default is not to use systemd for cgroups because the delegate issues still
# exists and systemd currently does not support the cgroup feature set required
# for containers run by docker
ExecStart=/usr/bin/dockerd -H fd://
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutStartSec=0
RestartSec=2
Restart=always

# Note that StartLimit* options were moved from "Service" to "Unit" in systemd 229.
# Both the old, and new location are accepted by systemd 229 and up, so using the old location
# to make them work for either version of systemd.
StartLimitBurst=3

# Note that StartLimitInterval was renamed to StartLimitIntervalSec in systemd 230.
# Both the old, and new name are accepted by systemd 230 and up, so using the old name to make
# this option work for either version of systemd.
StartLimitInterval=60s

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not support it.
# Only systemd 226 and above support this option.
TasksMax=infinity

# set delegate yes so that systemd does not reset the cgroups of docker containers
Delegate=yes

# kill only the docker process, not all processes in the cgroup
KillMode=process
OOMScoreAdjust=-500

[Install]
WantedBy=multi-user.target
EOF

cat << EOF > /etc/systemd/system/docker.socket
[Unit]
Description=Docker Socket for the API

[Socket]
ListenStream=/var/run/docker.sock
SocketMode=0660
SocketUser=root
SocketGroup=root

[Install]
WantedBy=sockets.target
EOF

systemctl enable docker.service
systemctl start docker.service
