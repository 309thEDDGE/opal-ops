from pathlib import Path
import os
import json

import pytest
from unittest.mock import Mock, patch, call

from validate_out_json import OutJsonValidator


def assert_not_called_with(self, *args, **kwargs):
    try:
        self.assert_called_with(*args, **kwargs)
    except AssertionError:
        return
    raise AssertionError('Expected %s to not have been called.' % self._format_mock_call_signature(args, kwargs))

Mock.assert_not_called_with = assert_not_called_with


@pytest.fixture
def contextTemplate():
    template = {
        'deployment_name': 'opal',
        'dns_base': '.127.0.0.1.nip.io',
        'mod_base': '.opal.127.0.0.1.nip.io',
        'banner_color': 'green',
        'banner_text': 'Unclassified (No CUI)',
        'deploy_keycloak': True,
        'deploy_minio': True,
        'external_keycloak_url': '',
        'keycloak_realm': 'master',
        'keycloak_secret': '',
        'external_minio_url': '',
    }
    return template

@pytest.fixture
def goodContext():
    good_context = {
        'deployment_name': 'good',
        'dns_base': '.good.base',
        'mod_base': '.opal.good.base',
        'banner_color': 'blue',
        'banner_text': 'this is green',
        'deploy_keycloak': True,
        'deploy_minio': True,
        'external_keycloak_url': 'keycloak.opal.good.base',
        'keycloak_realm': 'test-realm',
        'keycloak_secret': '1234554321',
        'external_minio_url': 'minio.opal.good.base:9000',
    }
    return good_context



class TestJsonValidator:
    def test_fill_missing_fields_fills_missing_fields(
        self, contextTemplate
    ):
        empty_context = {}

        validator = OutJsonValidator(empty_context, contextTemplate)
        validator.fill_missing_fields()

        assert validator.context_data == contextTemplate


    def test_fill_missing_fields_does_nothing_on_good_input(
            self, contextTemplate, goodContext
    ):

        validator = OutJsonValidator(goodContext, contextTemplate)
        validator.fill_missing_fields()

        assert validator.context_data == goodContext

    def test_validate_type_fixes_bad_types(self, contextTemplate):
        bad_context = {
            'deployment_name': True,
            'dns_base': '.127.0.0.1.nip.io',
            'mod_base': 'good stuff',
            'banner_color': 'blue',
            'banner_text': 4,
            'deploy_keycloak': 'yes',
            'deploy_minio': 1.03,
            'external_keycloak_url': 'https://keycloak-dev.opalacceptance.nip.io',
            'keycloak_realm': 'test-realm',
            'keycloak_secret': False,
            'external_minio_url': ['too', 'many', 'minio'],
        }

        validator = OutJsonValidator(bad_context, contextTemplate)

        validator.validate_field_types()

        for field in contextTemplate:
            assert type(validator.context_data[field]) == type(
                contextTemplate[field]
            )

    def test_validate_type_does_nothing_on_good_input(self, contextTemplate, goodContext):
        validator = OutJsonValidator(goodContext, contextTemplate)

        validator.validate_field_types()

        assert validator.context_data == goodContext

    @patch('make_context.ask', return_value='keycloak.opal.good.base')
    def test_string_not_empty_empty_string(self, mock_ask, contextTemplate):
        bad_context = {'external_keycloak_url': ''}
        keycloak_template = {'external_keycloak_url': 'keycloak.opal.good.base'}

        validator = OutJsonValidator(bad_context, keycloak_template)

        validator.check_string_not_empty('external_keycloak_url')

        mock_ask.assert_called()

        assert validator.context_data['external_keycloak_url'] == keycloak_template['external_keycloak_url']

    @patch('make_context.ask', return_value='uhoh.jpg')
    def test_string_not_empty_does_nothing_on_good_string(self, mock_ask, contextTemplate):
        bad_context = {'external_keycloak_url': 'keycloak.opal.good.base'}
        keycloak_template = {'external_keycloak_url': 'keycloak.opal.good.base'}

        validator = OutJsonValidator(bad_context, keycloak_template)

        validator.check_string_not_empty('external_keycloak_url')

        mock_ask.assert_not_called()

        assert validator.context_data['external_keycloak_url'] != 'uhoh.jpg'


    @patch('make_context.ask', return_value="bingo")
    def test_check_keycloak_minio_all_strings_empty(self, mock_ask, goodContext):
        in_context = {"external_keycloak_url": '',
                      "external_minio_url": '',
                      "keycloak_secret": ''}

        validator = OutJsonValidator(in_context, goodContext)

        validator.check_keycloak_minio()

        assert mock_ask.call_count == 3

        assert validator.context_data['external_keycloak_url'] == 'bingo'
        assert validator.context_data['external_minio_url'] == 'bingo'
        assert validator.context_data['keycloak_secret'] == 'bingo'


    @patch('make_context.ask', return_value="bingo")
    def test_check_keycloak_minio_two_strings_empty(self, mock_ask, goodContext):
        in_context = {"external_keycloak_url": 'good',
                      "external_minio_url": '',
                      "keycloak_secret": ''}

        validator = OutJsonValidator(in_context, goodContext)

        validator.check_keycloak_minio()

        assert mock_ask.call_count == 2

        assert validator.context_data['external_keycloak_url'] == 'good'
        assert validator.context_data['external_minio_url'] == 'bingo'
        assert validator.context_data['keycloak_secret'] == 'bingo'

    @patch('make_context.ask', return_value="bingo")
    def test_check_keycloak_minio_one_string_empty(self, mock_ask, goodContext):
        in_context = {"external_keycloak_url": 'good',
                      "external_minio_url": 'good',
                      "keycloak_secret": ''}

        validator = OutJsonValidator(in_context, goodContext)

        validator.check_keycloak_minio()

        assert mock_ask.call_count == 1

        assert validator.context_data['external_keycloak_url'] == 'good'
        assert validator.context_data['external_minio_url'] == 'good'
        assert validator.context_data['keycloak_secret'] == 'bingo'

    @patch('make_context.ask', return_value="bingo")
    def test_check_keycloak_blank_minio_both_strings_empty(self, mock_ask, goodContext):
        in_context = {"external_keycloak_url": '',
                      "external_minio_url": 'should be empty',
                      "keycloak_secret": ''}

        validator = OutJsonValidator(in_context, goodContext)

        validator.check_keycloak_blank_minio()

        assert mock_ask.call_count == 2

        assert validator.context_data['external_keycloak_url'] == 'bingo'
        assert validator.context_data['external_minio_url'] == ''
        assert validator.context_data['keycloak_secret'] == 'bingo'

    @patch('make_context.ask', return_value="bingo")
    def test_check_keycloak_blank_minio_one_strings_empty(self, mock_ask, goodContext):
        in_context = {"external_keycloak_url": 'good',
                      "external_minio_url": 'should be empty',
                      "keycloak_secret": ''}

        validator = OutJsonValidator(in_context, goodContext)

        validator.check_keycloak_blank_minio()

        assert mock_ask.call_count == 1

        assert validator.context_data['external_keycloak_url'] == 'good'
        assert validator.context_data['external_minio_url'] == ''
        assert validator.context_data['keycloak_secret'] == 'bingo'


    def test_blank_keycloak_minio(self, goodContext):
        in_context = {"external_keycloak_url": 'should be empty',
                      "external_minio_url": 'should also be empty',
                      "keycloak_secret": 'should also also be empty'}

        validator = OutJsonValidator(in_context, goodContext)

        validator.blank_keycloak_minio()

        assert validator.context_data['external_keycloak_url'] == ''
        assert validator.context_data['external_minio_url'] == ''
        assert validator.context_data['keycloak_secret'] == ''


    @patch.object(OutJsonValidator, 'blank_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_blank_minio')
    def test_validate_external_service_keycloak_true_minio_false(self, mock_blank_minio, mock_check_both, mock_blank_both):
        in_context = {"deploy_keycloak": True,
                      "deploy_minio": False}

        expected = {"deploy_keycloak": True,
                    "deploy_minio": True}

        validator = OutJsonValidator(in_context, expected)

        validator.validate_external_service()

        mock_blank_both.assert_called()
        mock_check_both.assert_not_called()
        mock_blank_minio.assert_not_called()

        assert validator.context_data == validator.template

    # Basically same as above, just with different truth value for deploy_minio from the start
    @patch.object(OutJsonValidator, 'blank_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_blank_minio')
    def test_validate_external_service_keycloak_true_minio_true(self, mock_blank_minio, mock_check_both, mock_blank_both):
        in_context = {"deploy_keycloak": True,
                      "deploy_minio": True}

        expected = {"deploy_keycloak": True,
                    "deploy_minio": True}

        validator = OutJsonValidator(in_context, expected)

        validator.validate_external_service()

        mock_blank_both.assert_called()
        mock_check_both.assert_not_called()
        mock_blank_minio.assert_not_called()

    @patch.object(OutJsonValidator, 'blank_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_blank_minio')
    def test_validate_external_service_keycloak_false_minio_false(self, mock_blank_minio, mock_check_both, mock_blank_both, contextTemplate):
        in_context = {"deploy_keycloak": False,
                      "deploy_minio": False}

        validator = OutJsonValidator(in_context, contextTemplate)

        validator.validate_external_service()

        mock_blank_both.assert_not_called()
        mock_check_both.assert_called()
        mock_blank_minio.assert_not_called()

    @patch.object(OutJsonValidator, 'blank_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_minio')
    @patch.object(OutJsonValidator, 'check_keycloak_blank_minio')
    def test_validate_external_service_keycloak_false_minio_true(self, mock_blank_minio, mock_check_both, mock_blank_both, contextTemplate):
        in_context = {"deploy_keycloak": False,
                      "deploy_minio": True}

        validator = OutJsonValidator(in_context, contextTemplate)

        validator.validate_external_service()

        mock_blank_both.assert_not_called()
        mock_check_both.assert_not_called()
        mock_blank_minio.assert_called()


    @patch('make_context.yes_no', return_value=False)
    def test_validate_dns_bad_mod_base_no_prepend(self, mock_yes_no, contextTemplate):
        bad_context = {
            'dns_base': '.127.0.0.1.nip.io',
            'mod_base': 'good stuff',
        }

        validator = OutJsonValidator(bad_context, contextTemplate)

        validator.validate_dns()

        mock_yes_no.assert_called()

        assert validator.context_data['dns_base'] == validator.context_data['mod_base']


    @patch('make_context.yes_no', return_value=True)
    def test_validate_dns_bad_mod_base_yes_prepend(self, mock_yes_no, contextTemplate):
        bad_context = {
            'dns_base': '.127.0.0.1.nip.io',
            'mod_base': 'good stuff',
        }

        validator = OutJsonValidator(bad_context, contextTemplate)

        validator.validate_dns()

        mock_yes_no.assert_called()

        assert validator.context_data['dns_base'] in validator.context_data['mod_base']
        assert validator.context_data['mod_base'] == validator.template['mod_base']


    @patch('make_context.yes_no', return_value=True)
    def test_validate_dns_good_mod_base_does_nothing(self, mock_yes_no, goodContext, contextTemplate):

        validator = OutJsonValidator(goodContext, contextTemplate)

        validator.validate_dns()

        mock_yes_no.assert_not_called()

        assert validator.context_data['mod_base'] == goodContext['mod_base']


    # This basically doesn't test anything, since all of the other tests cover the sub functions
    @patch.object(OutJsonValidator, 'fill_missing_fields')
    @patch.object(OutJsonValidator, 'validate_field_types')
    @patch.object(OutJsonValidator, 'validate_external_service')
    @patch.object(OutJsonValidator, 'validate_dns')
    def test_validate_json_runs_all_functions(self, mock_dns, mock_external_service, mock_field_types, mock_missing_fields, goodContext, contextTemplate):
        validator = OutJsonValidator(goodContext, contextTemplate)

        validator.validate_json()

        mock_dns.assert_called()
        mock_external_service.assert_called()
        mock_field_types.assert_called()
        mock_missing_fields.assert_called()
