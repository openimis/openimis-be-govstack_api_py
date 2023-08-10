from django.db import models


class Registry(models.Model):
    registry_name = models.CharField(
        max_length=255,
        help_text="Name of the registry, e.g., 'registryname'."
    )
    version = models.CharField(
        max_length=50,
        help_text="Version number of the registry, e.g., '111'."
    )
    class_name = models.CharField(
        max_length=255,
        help_text="Name of the class, e.g., 'InsureeRegistry'."
    )
    model = models.CharField(
        max_length=50,
        help_text="Model from candidate application that will be used to store data. Example: 'Insuree'"
    )
    fields_mapping = models.JSONField(
        help_text="Field mapping as a JSON object. Example: "
                  "{'ID': 'id', 'FirstName': 'otherNames', 'LastName': 'lastName', 'uuid': 'uuid'}."
    )
    special_fields = models.JSONField(
        help_text="Special fields that are not covered in a candidate application as a JSON list. Example: ['BirthCertificateID', 'PersonalData']."
    )
    default_values = models.JSONField(
        help_text="Default values as a JSON object. Example: "
                  "{'family_id': 'familyId: 1', 'gender_id': 'genderId: \"U\"', 'dob': '1920-04-02', 'head': 'head: false', 'card_issued': 'cardIssued: false'}."
    )
    mutations = models.JSONField(
        help_text="Mutations as a JSON object. Example: "
                  "{'create': 'createInsuree', 'delete': 'deleteInsurees', 'update': 'updateInsuree'}."
    )
    queries = models.JSONField(
        help_text="Queries as a JSON object. Example: {'get': 'GetInsurees'}."
    )
