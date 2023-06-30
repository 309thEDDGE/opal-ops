def format_shutdown_script(context):
    file = f"""#!/bin/bash

docker-compose -f docker-compose.yml -f {context['deployment_name']}.docker-compose.json down
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


    print(format_shutdown_script(context_data))