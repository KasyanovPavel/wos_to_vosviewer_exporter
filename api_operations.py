import requests


def validate_search_query(apikey, query):
    test_request = requests.get(
        url=f'https://wos-api.clarivate.com/api/wos/?databaseId=WOS&usrQuery={query}&'
            f'count=0&firstRecord=1',
        headers={'X-APIkey': apikey},
        timeout=16
    )
    if test_request.status_code == 200:
        return test_request.status_code, test_request.json()['QueryResult']['RecordsFound']
    return test_request.status_code, test_request.json()['message'].split(':')[-1]


def retrieve_wos_metadata_via_api(apikey, query, rpp, first_record=1):
    """Retrieve Web of Science documents metadata through Web of Science
    Expanded API.

    :param apikey: str.
    :param query: str.
    :param rpp: int.
    :param first_record: int.
    :return: dict.
    """
    params = {
        'databaseId': 'WOS',
        'usrQuery': query,
        'count': rpp,
        'firstRecord': first_record
    }
    initial_request = requests.get(
        url='https://wos-api.clarivate.com/api/wos',
        params=params,
        headers={'X-ApiKey': apikey},
        timeout=16
    )
    return initial_request.json()