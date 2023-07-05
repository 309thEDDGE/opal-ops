def format_start_script(context):
    file = f"""#!/bin/bash

FILE=./.env.secrets

if test -f "$FILE"; then
    echo "Found secret file. Deploying"
else
    echo "Secrets missing. Please copy the secrets template file and fill out the values"
    echo "The template can be copied like so:"
    echo "cp .env.secrets_template .env.secrets"
    exit 1
fi

mkdir -p ./jupyter_mounts/metaflow_metadata
chmod 777 -R ./jupyter_mounts

docker-compose -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json build
docker-compose -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json up -d
    """
    return file


if __name__ == "__main__": # pragma: no cover
    import sys
    import json
    import os

    if len(sys.argv) <= 1:
        this_fname = os.path.basename(__file__)
        print(f"usage: python {this_fname} [context_file.json]")
        exit(1)

    with open(sys.argv[1]) as f:
        context_data = json.load(f)


    print(format_start_script(context_data))
