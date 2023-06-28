def format_restart_script(context):
    file = f"""#!/bin/bash

# this does a full restart of opal to avoid any odd quirks that may be caused by docker-compose restart

docker-compose -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json down
docker-compose -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json up -d
    """
    return file


if __name__ == "__main__":
    import sys
    import json
    import os

    if len(sys.argv) <= 1:
        this_fname = os.path.basename(__file__)
        print(f"usage: python {this_fname} [context_file.json]")
        exit(1)

    with open(sys.argv[1]) as f:
        context_data = json.load(f)


    print(format_restart_script(context_data))