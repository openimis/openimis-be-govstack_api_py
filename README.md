# openIMIS Backend Report reference module
This repository holds the files of the openIMIS Backend Core reference module.
It is a required module of [openimis-be_py](https://github.com/openimis/openimis-be_py).

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

A module that serves to direct requests from building blocks and handle them using services available in openIMIS. By design, each building block has its own folder inside "govstack_test_harness_api/building_blocks".

Currently, only the folder for bb-digital-registries is available. After launching the application on the same port and initializing openIMIS, what remains is the handling of requests, which requires knowledge of the system and test specifications. Swagger has also been implemented, but it's solely for module development and its utility is limited to locally testing schemas.

In the bb-digital-registries module, endpoints concerning registries have been implemented, excluding the implementation of endpoints related to the creation and management of multiple databases.

## ORM mapping:
* 

## Listened Django Signals
None

## Services

## GraphQL Queries
None

## GraphQL Mutations - each mutation emits default signals and return standard error lists (cfr. openimis-be-core_py)
None

## Configuration options (can be changed via core.ModuleConfiguration)
None

## openIMIS Modules Dependencies
* core.models.UUIDModel
