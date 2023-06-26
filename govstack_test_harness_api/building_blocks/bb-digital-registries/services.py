from django.db.models import Q

from insuree.models import Insuree


def check_if_registry_exists(registryname, versionnumber, query_content) -> bool:

    # if not possible to check registry then pass

    filters = []
    if 'ID' in query_content:
        filters.append(Q(id=query_content['ID']))
    if 'FirstName' in query_content:
        filters.append(Q(other_names=query_content['FirstName']))
    if 'LastName' in query_content:
        filters.append(Q(last_name=query_content['LastName']))
    if 'BirthCertificateID' in query_content:
        filters.append(Q(json_ext=query_content['BirthCertificateID']))

    insuree_exists = Insuree.objects.filter(*filters).exists()

    return insuree_exists
