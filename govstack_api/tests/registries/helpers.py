import os

from django.contrib.auth import authenticate

from core.models import InteractiveUser, User
from core.services import create_or_update_user_roles
from govstack_api.models import Registry
from insuree.models import Insuree, Family, Gender, InsureePhoto


def create_default_registry(registry_name=None, version=None, class_name=None, model=None,
                            fields_mapping=None, special_fields=None, default_values=None,
                            mutations=None, queries=None):
    default_args = {
        "registry_name": 'registryname',
        "version": '111',
        "class_name": 'InsureeRegistry',
        "model": 'Insuree',
        "fields_mapping": {"ID": "id", "uuid": "uuid", "LastName": "lastName", "FirstName": "otherNames"},
        "special_fields": ["BirthCertificateID", "PersonalData"],
        "default_values": {
            "dob": 'dob: "1920-04-02"',
            "head": "head: false",
            "family_id": "familyId: 1",
            "gender_id": "genderId: \"M\"",
            "card_issued": "cardIssued: false"
        },
        "mutations": {"create": "createInsuree", "delete": "deleteInsurees", "update": "updateInsuree"},
        "queries": {"get": "insurees"}
    }

    return Registry.objects.create(
        registry_name=registry_name if registry_name is not None else default_args["registry_name"],
        version=version if version is not None else default_args["version"],
        class_name=class_name if class_name is not None else default_args["class_name"],
        model=model if model is not None else default_args["model"],
        fields_mapping=fields_mapping if fields_mapping is not None else default_args["fields_mapping"],
        special_fields=special_fields if special_fields is not None else default_args["special_fields"],
        default_values=default_values if default_values is not None else default_args["default_values"],
        mutations=mutations if mutations is not None else default_args["mutations"],
        queries=queries if queries is not None else default_args["queries"]
    )


def create_interactive_user_from_data(
        user_id,
        user_uuid,
        username=None,
        other_names=None,
        last_name=None,
        birth_certificate_id=None,
        password="Test1234",
        roles=None,
        custom_props=None
):
    username = os.getenv('login_openIMIS')
    password = os.getenv('password_openIMIS')

    if roles is None:
        roles = [3, 7]
    if username is None:
        username = other_names

    i_user = InteractiveUser.objects.create(
        **{
            "language_id": "en",
            "uuid": user_uuid,
            "last_name": last_name,
            "other_names": other_names,
            "login_name": username,
            "audit_user_id": -1,
            "role_id": roles[0]
        }
    )
    i_user.set_password(password)
    i_user.save()
    create_or_update_user_roles(i_user, roles, 1)
    return User.objects.create(username=username, i_user=i_user)


def create_test_insuree(
        with_family=True, is_head=False, custom_props=None, family_custom_props=None,
        last_name=None, other_names=None, insuree_id=None, json_ext=None):
    # insuree has a mandatory reference to family and family has a mandatory reference to insuree
    # So we first insert the family with a dummy id and then update it
    if with_family:
        family = Family.objects.create(
            validity_from="2019-01-01",
            head_insuree_id=1,  # dummy
            audit_user_id=-1,
            **(family_custom_props if family_custom_props else {})
        )

    else:
        family = None

    insuree = Insuree.objects.create(
        **{
            "last_name": "Lewiss",
            "id": 2007,
            "uuid": "93882137-25dc-4447-a648-6c598e0d4985",
            "other_names": "Othy",
            "chf_id": "2007",
            "family": Family.objects.get(id=1),
            "gender": Gender.objects.get(code='M'),
            "dob": "1920-04-02",
            "head": is_head,
            "card_issued": False,
            "validity_from": "2019-01-01",
            "audit_user_id": -1,
            "json_ext": json_ext,
            **(custom_props if custom_props else {})
        }
    )
    if with_family:
        family.head_insuree_id = insuree.id
        if family_custom_props:
            for k, v in family_custom_props.items():
                setattr(family, k, v)
        family.save()

    print(insuree)
    return insuree

