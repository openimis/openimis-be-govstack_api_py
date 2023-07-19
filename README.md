# Govstack API
If you want to add a new BB (Building Block), you would need to add a new package inside the "BBs" component in the govstack_api module. This package should include new registry classes that inherit from the BBPMI interface, new controller objects to manage the business logic, and possibly new views or serializers if necessary.

# Configuration
The configuration for each BB would be maintained within its respective class definitions in the package. This might include methods for mapping to and from GraphQL, executing business logic, and managing data. Depending on the requirements of the new BB, you might also need to add or modify methods in the Views (APIView), Serializer, and GenericRegistry objects.

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
## Listened Django Signals
None

## GraphQL Queries
None

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)
None

## openIMIS Modules Dependencies
* core.models.UUIDModel