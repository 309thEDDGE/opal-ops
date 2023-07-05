import json
import make_context
import pytest
from unittest.mock import patch

class TestMakeContext():

    @pytest.fixture
    def contextData(self):
       
        context = """{
            "deployment_name": "test_context",
            "dns_base": "",
            "mod_base": "",
            "banner_color": "Y",
            "banner_text": "orange",
            "singleuser_type": "singleuser",
            "deploy_keycloak": true,
            "deploy_minio": true,
            "keycloak_realm": "master",
            "keycloak_secret":"0000000000000000000000000000000000000000000000000000000000000000",    
            "external_minio_url": "external/minio_url",
            "external_keycloak_url": "https://externalURL"
        }"""
        context_json = json.loads(context)
        return context_json
    
    @patch("builtins.input", return_value="Whatever we want it to return")
    def test_ask(self,input):
        expected = "Whatever we want it to return"
        actual = make_context.ask(question="Enter a String: ", 
                                  validating_regex=".*", 
                                  invalid_response="Invalid Response"
                                  )
        assert actual == expected

    yesNo_data = [("Y", True),("n", False),("", True)]
    
    @pytest.mark.parametrize("inputVar, expected", yesNo_data)
    def test_yes_no(self, inputVar, expected):

        @patch("builtins.input", return_value=inputVar)
        def test(input):
            actual = make_context.yes_no(question="[Y/n]")
            assert actual == expected

        test()

        
