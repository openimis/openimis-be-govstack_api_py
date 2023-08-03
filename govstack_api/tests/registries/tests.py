import json
from audioop import reverse
from django.test import TestCase, Client
from django.urls import reverse
from govstack_api.tests.registries.helpers import (
    create_default_registry, create_interactive_user_from_data, create_test_insuree
)
from django.apps import apps

from insuree.models import Insuree

config = apps.get_app_config('govstack_api')


class ApiUrlsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.headers = {
            'HTTP_ACCEPT': 'application/json',
            'CONTENT_TYPE': 'application/json',
            'HTTP_INFORMATION_MEDIATOR_CLIENT': config.IM_CLIENT,
        }
        self.registry = create_default_registry()
        self.user = create_interactive_user_from_data(
            user_id=2001, user_uuid="3213-d33d-ds22-d11d-d55d", last_name='John', other_names='Johnny'
        )
        self.insuree = create_test_insuree(
            last_name="Lewiss",
            other_names="Othy",
            insuree_id=2007,
            json_ext='{"BirthCertificateID": "B12DC3", "PersonalData": {"some": "data"}}')
        self.insuree.save()

    def test_read_registry_record(self):
        url = reverse('read_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "Lewiss",
                    "BirthCertificateID": "B12DC3",
                    "PersonalData": {"some": "data"}
                }
            }
        }
        data = json.dumps(data)
        response = self.client.post(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)
        self.assertEqual(response.json()['content'], second={
            "ID": "2007",
            "FirstName": "Othy",
            "LastName": "Lewiss",
            "BirthCertificateID": "B12DC3",
            "PersonalData": {"some": "data"}
        })

    def test_registry_record_exists(self):
        url = reverse('check_registry_record_presence', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "Lewiss",
                    "BirthCertificateID": "B12DC3",
                    "PersonalData": {"some": "data"}
                }
            }
        }
        data = json.dumps(data)
        response = self.client.post(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)
        self.assertEqual(response.json(), second={'answer': {'status': True, 'message': 'Object found from database'}})

    def test_registry_record_does_not_exist(self):
        url = reverse('check_registry_record_presence', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "53125",
                    "FirstName": "Othy",
                    "LastName": "Lewiss",
                    "BirthCertificateID": "B12DC3",
                    "PersonalData": {"some": "data"}
                }
            }
        }
        data = json.dumps(data)
        response = self.client.post(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=404)

    def test_can_read_specific_field_from_registry_record(self):
        url = reverse(
            'read_field_from_registry_record',
            kwargs={
                'registryname': 'registryname',
                'versionnumber': '111',
                'uuid': self.insuree.uuid,
                'field': 'lastName',
                'ext': 'json'
            })
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"lastName": "Lewiss"})

    def test_registry_record_update_successful(self):
        url = reverse('update_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "Lewiss",
                }
            },
            "write": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "LewissAAA",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.put(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)

    def test_registry_record_update_bad_request(self):
        url = reverse('update_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "find": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "Lewiss",
                }
            },
            "save": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "LewissAAA",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.put(url, data, content_type='application/json', **self.headers)
        self.insuree.save()
        self.assertEqual(response.status_code, second=400)

    def test_registry_record_create_succesful(self):
        url = reverse('create_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "write": {
                "content": {
                    "ID": "332012",
                    "FirstName": "JOHN",
                    "LastName": "PAYLO",
                    "BirthCertificateID": "B12DC3",
                    "PersonalData": {"some": "data"}
                }
            }
        }
        data = json.dumps(data)
        response = self.client.post(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)

    def test_registry_record_update_or_create_successful(self):
        url = reverse('update_or_create_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "Lewiss",
                }
            },
            "write": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Othy",
                    "LastName": "New_Last_Name",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.post(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)

    def test_registry_record_delete_succesful(self):
        url = reverse('delete_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111', "ID": "2007"})
        response = self.client.delete(url, data={}, content_type='application/json', **self.headers)
        print(Insuree.objects.get(id=2007))
        self.assertEqual(response.status_code, second=204)

