from django.db import migrations
def add_initial_record(apps, schema_editor):
    Registry = apps.get_model('govstack_api', 'Registry')
    Registry.objects.create(
        registry_name='registryname',
        version='111',
        class_name='InsureeRegistry',
        model='Insuree',
        id_field='chfId',
        fields_mapping={
            "ID": "id",
            "uuid": "uuid",
            "LastName": "lastName",
            "FirstName": "otherNames",
            "phone": "phone",
            "CurrentAddress": "currentAddress"
        },
        special_fields=["BirthCertificateID", "PersonalData"],
        default_values={
            "otherNames": "otherNames: \"undefined\"",
            "family_id": "familyId: 1",
            "gender_id": "genderId: \"O\"",
            "dob": "dob: \"1920-04-02\"",
            "head": "head: false",
            "card_issued": "cardIssued: false"
        },
        mutations={
            "create": "createInsuree",
            "delete": "deleteInsurees",
            "update": "updateInsuree"
        },
        queries={
            "get": "insurees"
        }
    )
def remove_initial_record(apps, schema_editor):
    Registry = apps.get_model('govstack_api', 'Registry')
    Registry.objects.filter(
        registry_name='registryname',
        version='111',
        class_name='InsureeRegistry',
        id_field='chfId'
    ).delete()
class Migration(migrations.Migration):
    dependencies = [
        ('govstack_api', '0003_alter_registry_id_field'),
    ]
    operations = [
        migrations.RunPython(add_initial_record, reverse_code=remove_initial_record),
    ]