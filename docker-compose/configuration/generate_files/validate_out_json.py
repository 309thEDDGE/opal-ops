import sys
import json
import os
import logging
import make_context


class OutJsonValidator:
    def __init__(self, in_context_data, in_template, in_f_path="out.json"):
        self.context_data = in_context_data
        self.template = in_template
        # print(self.template)
        self.f_path = in_f_path

    # Not so much a proper validation since we need an external library for jsonschema,
    # so this is more of a "set missing values to reasonable defaults"
    # nip.io won't work as the dns/mod base in airgapped situations, but it should be reasonable enough elsewhere
    def validate_json(self):
        self.fill_missing_fields()
        # basic type checking
        self.validate_field_types()
        # checks dependent fields look right for keycloak/minio
        self.validate_external_service()
        # checks dns fields are related
        self.validate_dns()

        return self.context_data

    # There are a handful of cases to expect when connecting to remote minio/keycloak servers,
    # the following checks make sure dependent fields have the correct values or are blanked if unneeded
    # This likely won't do anything in most cases, unless you're building your out.json manually (and incorrectly)
    def validate_external_service(self):
        # Minio must be deployed if not connecting to an external keycloak server
        # minio == false, keycloak == true
        if (
            self.context_data['deploy_minio'] == False
            and self.context_data['deploy_keycloak'] == True
        ):
            logging.debug(
                "Minio must be deployed with Keycloak, setting field 'deploy_minio' to 'True'"
            )
            self.context_data['deploy_minio'] = True
        # minio == true, keycloak == true
        if (
            self.context_data['deploy_minio'] == True
            and self.context_data['deploy_keycloak'] == True
        ):
            self.blank_keycloak_minio()
        # minio == false, keycloak == false
        elif (
            self.context_data['deploy_minio'] == False
            and self.context_data['deploy_keycloak'] == False
        ):
            self.check_keycloak_minio()
        # minio == true, keycloak == false
        elif (
            self.context_data['deploy_minio'] == True
            and self.context_data['deploy_keycloak'] == False
        ):
            self.check_keycloak_blank_minio()

        # need to make sure external service fields aren't empty if we're connecting to them

    # Very same-y functions, but it cleans up external_service_validator for testing
    def check_keycloak_minio(self):
        logging.debug('checking external service values')
        self.check_string_not_empty(
            'external_keycloak_url'
        )
        self.check_string_not_empty(
            'keycloak_secret'
        )
        self.check_string_not_empty(
            'external_minio_url'
        )

    def check_keycloak_blank_minio(self):
        logging.debug('checking external service values')
        self.check_string_not_empty(
            'external_keycloak_url'
        )
        self.check_string_not_empty(
            'keycloak_secret'
        )
        self.context_data['external_minio_url'] = ''

    def blank_keycloak_minio(self):
        # Since we're not connecting to external minio/keycloak instances, we'll set
        # the fields for those to empty strings to avoid any confusion
        logging.debug('Blanking unneeded external service fields')
        self.context_data['external_keycloak_url'] = ''
        self.context_data['keycloak_secret'] = ''
        self.context_data['external_minio_url'] = ''

    def check_string_not_empty(self, field):
        while True:
            if len(self.context_data[field]) == 0:
                logging.error(
                    'Field {0} is empty, please enter a value'.format(field)
                )
                self.context_data[field] = make_context.ask(f'{field}: ')
                # self.ask_new_field_value(field)
            else:
                break

    # mod_base needs to be a superstring of dns_base, or services won't run
    def validate_dns(self):
        if self.context_data['dns_base'] not in self.context_data['mod_base']:
            logging.warning(
                'Field `dns_base` is not a substring of `mod_base`. Reverting `mod_base` to `dns_base` value {0}.'.format(
                    self.context_data['dns_base']
                )
                # "If this is a mistake, prepend '.opal' to mod_base and re-run new_deployment.bash.".format(context_data["dns_base"])
            )
            if make_context.yes_no(
                "Would you like to prepend '.opal' to the dns basename? [Y/n]"
            ):
                self.context_data['mod_base'] = (
                    '.opal' + self.context_data['dns_base']
                )
            else:
                self.context_data['mod_base'] = self.context_data['dns_base']

    # Fields missing from input json will be replaced with the template value
    def fill_missing_fields(self):
        for field in self.template:
            if field not in self.context_data:
                self.context_data[field] = self.template[field]

    # Fields with a type differing from the template will be replaced with the template value
    def validate_field_types(self):
        # there's no reason to expect nested dictionaries, so a simple for loop will suffice
        for field in self.template:
            d_val = self.context_data[field]
            t_val = self.template[field]
            t_type = type(t_val)
            logging.debug(
                'Validating <{0}> value at field: {1}'.format(
                    t_type.__name__, field
                )
            )
            if not isinstance(d_val, t_type):
                logging.info(
                    "Field '{0}': Expected type <str>, got <{1}> ({2}). Setting to default "
                    "value of '{3}'\n"
                    'If you would like to change this field, please edit {4} with the desired value and re-run new_deployment.bash'.format(
                        field, type(d_val).__name__, d_val, t_val, self.f_path
                    )
                )
                self.context_data[field] = self.template[field]

        # disabled along with ask_new_field_value
#            if make_context.yes_no("Change value? [Y/n]"):
#                self.ask_new_field_value(field)
#            else:
#                self.context_data[field] = self.template[field]


# Temporarily disabled due to major scope creep
#    def ask_new_field_value(self,field):
#        expected_type = type(self.template[field])
#        switch = {
#
#        }
#        while True:
#            new_field = make_context.ask(f"{field}: ")
#            if type(new_field) == expected_type:
#                self.context_data[field] = new_field
#                break
#            else:
#                logger.warning("Input {0} is not of expected type {1}, please try again".format(new_field, expected_type))


# def safe_exit(context_data,error):
#    logging.error(error)


if __name__ == '__main__': # pragma: no cover

    logging.basicConfig(level=logging.WARNING, format='%(levelname)s:%(message)s')

    full_cwd = os.getcwd()

    template = {
        'deployment_name': 'opal',
        'dns_base': '.127.0.0.1.nip.io',
        'mod_base': '.127.0.0.1.nip.io',
        'banner_color': 'green',
        'banner_text': 'Unclassified (No CUI)',
        'deploy_keycloak': True,
        'deploy_minio': True,
        'external_keycloak_url': '',
        'keycloak_realm': 'master',
        'keycloak_secret': '',
        'external_minio_url': '',
    }

    if len(sys.argv) <= 1:
        this_fname = os.path.basename(__file__)
        logging.debug(f'usage: python {this_fname} [context_file.json]')
        exit(1)

    context_file = sys.argv[1]

    with open(context_file) as f:
        context_data = json.load(f)

    validator = OutJsonValidator(context_data, template, context_file)

    print('=== OPAL Configuration Validation Tool ===')
    new_json = validator.validate_json()
    print('--------- Staged changes ---------')
    print(json.dumps(new_json, indent=4))

    if make_context.yes_no('Write changes to {0}? [Y/n]'.format(context_file)):
        with open(context_file, 'w') as f:
            json.dump(context_data, f, indent=4)
        # write_new_out(context_data)
