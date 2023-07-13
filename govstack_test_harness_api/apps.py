from django.apps import AppConfig


class TestHarnessApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'govstack_test_harness_api'

    digital_registry = {
        "birth_registry": {
            "1": {
                'ID': 'ID'
            }
        },
        "registryname": {
            "111": {
                'ID': 'chfId',
                'FirstName': 'otherNames',
                'LastName': 'lastName',
                'BirthCertificateID': 'json_ext'
            }
        }
    }