def format_service_stop_file(context, full_cwd):
    file = f"""[Unit]
Description=OPAL Datascience Platform Stop Service
Before=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
TimeoutStopSec=120
ExecStop=/bin/bash -c "cd {full_cwd} && docker-compose -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json down --remove-orphans"
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=OPAL_Stop

[Install]
WantedBy=multi-user.target
    """
    return file




if __name__ == "__main__":
    import sys
    import json
    import os

    full_cwd = os.getcwd()
    # parent_dir = os.path.dirname(os.getcwd())

    if len(sys.argv) <= 1:
        this_fname = os.path.basename(__file__)
        print(f"usage: python {this_fname} [context_file.json]")
        exit(1)

    

    with open(sys.argv[1]) as f:
        context_data = json.load(f)


    print(format_service_stop_file(context_data, full_cwd))