#! /bin/bash

LOG_FILE=/home/jovyan/startup.log
log_to_file () {
    echo "$1 (exit value: $?)" | tee $LOG_FILE
}
touch $LOG_FILE

# start of actual setup steps
echo "-------------" >> $LOG_FILE
date >> $LOG_FILE
log_to_file "Start setup"

# 1
tar -xf /tmp/tars/jhub-conf.tar -C /opt
log_to_file "Copy jupyterhub config directory"

# 2
conda init bash
log_to_file "Initialize conda"

# 3
echo 'source /home/jovyan/.bashrc && conda activate singleuser' > /home/jovyan/.profile
log_to_file "Add conda activate to .profile"

# 4
cp -r /opt/config/opalbanner /opt/conda/envs/singleuser/share/jupyter/labextensions
bash /opt/config/init_banner.bash "$OPAL_BANNER_TEXT" "$OPAL_BANNER_COLOR"
log_to_file "Initialize banner extension"

# 5
ln -sfn /opt/data/opal /home/jovyan/opal
log_to_file "Link directories to home"

# 6
mkdir -p /home/jovyan/.metaflowconfig
envsubst < /opt/config/metaflow_config.json > /home/jovyan/.metaflowconfig/config.json
log_to_file "Fill in metaflow config file"

# 7
python /opt/config/python_setup.py
log_to_file "Custom python setup"

# Start the singleuser server (has to be last)
/usr/local/bin/start-singleuser.sh
