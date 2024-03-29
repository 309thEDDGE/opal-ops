from importer import dynamic_module_import
module = dynamic_module_import('make_context')

import pytest
from unittest.mock import patch

class TestMakeContext():

    @pytest.fixture
    def contextData(self):

        context = {
            "deployment_name": "test_context",
            "dns_base": "",
            "mod_base": "",
            "banner_color": "GREEN",
            "banner_text": "UNCLASSIFIED",
            "singleuser_type": "singleuser",
            "deploy_keycloak": True,
            "deploy_minio": True,
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://keycloak.opalacceptance.dso.mil",
            "keycloak_realm": "master"
        }

        return context
       

    
    @patch("builtins.input", return_value="Whatever we want it to return")
    def test_ask(self,input):
        expected = "Whatever we want it to return"
        actual = module.ask(question="Enter a String: ", 
                                  validating_regex=".*", 
                                  invalid_response="Invalid Response"
                                  )
        assert actual == expected

    yesNo_data = [("Y", True),("n", False),("", True)]
    
    @pytest.mark.parametrize("inputVar, expected", yesNo_data)
    def test_yes_no(self, inputVar, expected):

        @patch("builtins.input", return_value=inputVar)
        def test(input):
            actual = module.yes_no(question="[Y/n]")
            assert actual == expected

        test()
