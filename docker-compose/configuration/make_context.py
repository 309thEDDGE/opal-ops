import re
import json
from pathlib import Path
import sys

# asks a question and gets a response from the user
def ask(
    question="Enter a String: ", 
    validating_regex=".*", 
    invalid_response="Invalid Response",
    **kwargs # unused, don't worry about it
    ):
    while True:
        print(question)
        out = input()
        if not re.search(validating_regex, out):
            print(invalid_response)
        else:
            return out

def yes_no(
    question="[Y/n]"
):
    print(question)
    valid_input = False
    in_bool=False
    while not valid_input:
        try:
            reply = str(input()).lower()
            if reply == 'y' or reply == '': 
                in_bool=True
                valid_input = True
            elif reply == 'n':
                in_bool = False
                valid_input = True
            else: raise Exception("Unrecognized input, please try again")
        except Exception as e:
            print(str(e))
            continue
    return in_bool


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("usage: python make_context.py [output_file.json]")
        exit(1)

    context = {}

    # What... is your name?
    context["deployment_name"] = ask(
        "Deployment name (i.e acceptance, cui, etc)",
        "[a-zA-Z1-9_]+",
        "Deployment name can only be alphanumeric + underscore"
    )

    # What... is your quest?
    context["dns_base"] = ""
    context["mod_base"] = ""
    if yes_no("Localhost deployment? [Y/n]\n(Use this if this deployment is not meant to be served to users)"):
        print("Be sure to add\n\n  127.0.0.1 keycloak\n  127.0.0.1 minio\n  127.0.0.1 opal\n\nto /etc/hosts")
    else:
        context["dns_base"] = ask(
            "Base DNS name of this deployment (i.e .companyname.com) )",
            "^\\.[\\w\\.]*" # starts with '.', contains nonly on-whitespace and '.'
        )
        context["mod_base"] = context["dns_base"]
        # add 'opal' to the base url 
        # (this allows for us to have a distinct keycloak/minio in case another exists on the network)
        if yes_no("Add opal to base url? [Y/n]\n(Use if you already have keycloak or minio deployed elsewhere on the network)"):
            print(f"You can reach additional services at [service].opal.{context['dns_base']}")
            context["mod_base"] = ".opal" + context["dns_base"]


    # What... is your favorite color?
    context["banner_color"] = ask(
        "Banner color (Looks like classification banner, must be HTML color): "
    )

    context["banner_text"] = ask(
        "Banner text (Can be used for network name or classification markings)"
    )

    # ask if the user wants to use the dev singleuser build
    context["singleuser_type"] = "singleuser_dev"
    if not yes_no("Use lightweight singleuser image? [Y/n]\n(This is primarily for local dev setups)"):
        context["singleuser_type"] = "singleuser"

    # not concerned with external LDAP right now
    context["deploy_keycloak"] = True
    context["deploy_minio"] = True
    # context["deploy_keycloak"] = "yes" == ask(
    #     "Deploy keycloak with OPAL? (yes/no) ",
    #     "(yes|no)",
    #     "yes or no"
    # )

    # if not context["deploy_keycloak"]:
    #     context["external_keycloak_url"] = ask(
    #         "External keycloak API (i.e keycloak.companyname.com:1234): "
    #     )

    # context["deploy_minio"] = "yes" == ask(
    #     "Deploy minio with OPAL? (yes/no) ",
    #     "(yes|no)",
    #     "yes or no"
    # )

    # if not context["deploy_minio"]:
    #     context["external_minio_url"] = ask(
    #         "External minio url (i.e minio.companyname.com:9000): "
    #     )
    
    # save as json file somewhere
    with open(sys.argv[1], "w") as f:
        json.dump(context, f, indent=4)