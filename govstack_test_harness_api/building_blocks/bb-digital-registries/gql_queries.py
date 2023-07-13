def get_update_registry_query(uuid="", chf_id="", update_fields="") -> str:
    query = f'''
                mutation {{
                  updateInsuree(
                    input: {{
                      clientMutationId: "552f8e55-ed5a-4e1e-a159-ea8f8cec0560"
                      clientMutationLabel: "Update insuree"
                      uuid: "{uuid}"
                      chfId: "{chf_id}"
                {update_fields}
                genderId: "F"
                head: true
                dob: "1974-06-11"
                cardIssued:false
                familyId: 1
                relationshipId: 4
                    }}
                  ) {{
                    clientMutationId
                    internalId
                  }}
                }}
                '''
    return query


def get_insurees_query(variable_values: str = "", fetched_fields: str = "") -> str:
    return f'''
            query GetInsurees {{
                insurees({variable_values}) {{
                    edges{{
                        node{{
                            {fetched_fields}
                        }}
                    }}
                }}
            }}
            '''


def create_insurees_query(variables: dict) -> str:
    return f'''
    mutation {{
        createInsuree(
            input: {{
                clientMutationLabel: "{variables['clientMutationLabel']}"
                chfId: "{variables['chfId']}"
                lastName: "{variables['lastName']}"
                otherNames: "{variables['otherNames']}"
                genderId: "{variables['genderId']}"
                dob: "{variables['dob']}"
                head: {str(variables['head']).lower()}
                cardIssued: {str(variables['cardIssued']).lower()}
                jsonExt: "{variables['jsonExt']}"
                familyId: 1
            }}
        ) {{
            clientMutationId
            internalId
        }}
    }}
    '''


def delete_insuree_query(uuid):
    return f'''mutation
    {{
        deleteInsurees(
            input: {{
            clientMutationId: "c164412c-45a6-4f3f-8a2b-4290739751e2"
            clientMutationLabel: "Delete insuree"

            uuid: "{uuid}", uuids: ["{uuid}"]
        }}
    ) {{
        clientMutationId
    internalId
    }}
    }}
    '''
