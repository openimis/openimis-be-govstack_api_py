import json

from django.apps import apps
from django.test import TestCase, Client
from django.urls import reverse
from urllib.parse import urlencode
from insuree.models import Insuree

from govstack_api.tests.registries.helpers import (
    create_default_registry, create_interactive_user_from_data, create_test_insuree
)

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
            other_names="Smith",
            insuree_id=2007,
            json_ext='{"BirthCertificateID": "B12DC3", "PersonalData": {"some": "data"}}')
        self.insuree.save()

    def test_read_registry_record(self):
        url = reverse(viewname='read_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
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
            "FirstName": "Smith",
            "LastName": "Lewiss",
            "BirthCertificateID": "B12DC3",
            "PersonalData": {"some": "data"}
        })

    def test_registry_record_exists(self):
        url = reverse(viewname='check_registry_record_presence', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
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
        url = reverse(viewname='check_registry_record_presence', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "53125",
                    "FirstName": "Smith",
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
            viewname='read_field_from_registry_record',
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
        url = reverse(viewname='update_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
                    "LastName": "Lewiss",
                }
            },
            "write": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
                    "LastName": "LewissAAA",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.put(url, data, content_type='application/json', **self.headers)
        self.assertEqual(
            first="LewissAAA",
            second=Insuree.objects.filter(last_name="LewissAAA").values_list('last_name', flat=True).first()
        )
        self.assertEqual(response.status_code, second=200)

    def test_registry_record_update_bad_request(self):
        url = reverse(viewname='update_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "find": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
                    "LastName": "Lewiss",
                }
            },
            "save": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
                    "LastName": "LewissAAA",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.put(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=400)

    def test_registry_record_create_succesful(self):
        url = reverse(viewname='create_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
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
        url = reverse(viewname='update_or_create_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111'})
        data = {
            "query": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
                    "LastName": "Lewiss",
                }
            },
            "write": {
                "content": {
                    "ID": "2007",
                    "FirstName": "Smith",
                    "LastName": "New_Last_Name",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.post(url, data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)

    def test_registry_record_delete_succesful(self):
        url = reverse(viewname='delete_registry_record', kwargs={'registryname': 'registryname', 'versionnumber': '111', "ID": "2007"})
        response = self.client.delete(url, data={}, content_type='application/json', **self.headers)
        self.assertTrue(Insuree.objects.filter(id=2007, validity_to__isnull=False).exists())
        self.assertEqual(response.status_code, second=204)

    def test_registry_records_retrieve_list(self):
        insuree_first = create_test_insuree(
            last_name="John",
            other_names="Max",
            insuree_id=2008,
            json_ext='{"BirthCertificateID": "B12DC3", "PersonalData": {"some": "data"}}'
        )
        insuree_second = create_test_insuree(
            last_name="John",
            other_names="Luap",
            insuree_id=2009,
            json_ext='{"BirthCertificateID": "B72DC3", "PersonalData": {"some": "data"}}'
        )
        self.assertTrue(Insuree.objects.filter(id=2008, validity_to__isnull=True).exists())
        self.assertTrue(Insuree.objects.filter(id=2009, validity_to__isnull=True).exists())
        base_url = reverse(
            viewname='list_registry_records',
            kwargs={
                'registryname': 'registryname',
                'versionnumber': '111',
            }
        )
        query_params = urlencode({
            'search': "John",
            'filter': "LastName",
            'ordering': 'descending',
            'page': 1,
            'page_size': 2,
            'query.<fieldname>': "string"
        })
        url = f"{base_url}?{query_params}"
        response = self.client.get(url, content_type='application/json', **self.headers)
        self.assertEqual(response.data.get('count'), 2)

    def test_registry_records_update_sucesful(self):
        create_test_insuree(
            last_name="John",
            other_names="Max",
            insuree_id=2008,
            json_ext='{"BirthCertificateID": "B12DC3", "PersonalData": {"some": "data"}}'
        )
        create_test_insuree(
            last_name="John",
            other_names="Luap",
            insuree_id=2009,
            json_ext='{"BirthCertificateID": "B72DC3", "PersonalData": {"some": "data"}}'
        )
        self.assertTrue(Insuree.objects.filter(id=2008, validity_to__isnull=True).exists())
        self.assertTrue(Insuree.objects.filter(id=2009, validity_to__isnull=True).exists())
        url = reverse(
            viewname='list_registry_records',
            kwargs={
                'registryname': 'registryname',
                'versionnumber': '111',
            }
        )
        data = {
            "query": {
                "content": {
                    "LastName": "John",
                }
            },
            "write": {
                "content": {
                    "FirstName": "New_John_First_Name",
                    "LastName": "John",
                }
            }
        }
        data = json.dumps(data)
        response = self.client.put(url, data=data, content_type='application/json', **self.headers)
        self.assertEqual(response.status_code, second=200)
        self.assertEqual(
            first=2,
            second=Insuree.objects.filter(other_names="New_John_First_Name")
            .values_list("other_names", flat=True)
            .count(),
        )
        self.assertEqual(
            first=Insuree.objects.filter(id=2008, other_names="New_John_First_Name")
            .values_list("other_names", flat=True)
            .first(),
            second="New_John_First_Name",
        )
        self.assertEqual(
            Insuree.objects.filter(id=2009, other_names="New_John_First_Name")
            .values_list("other_names", flat=True)
            .first(),
            second="New_John_First_Name",
        )
