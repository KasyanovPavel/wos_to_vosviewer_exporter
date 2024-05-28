from datetime import date
from flask import Flask, render_template, request
from apikeys import EXPANDED_APIKEY
from api_operations import validate_search_query, retrieve_wos_metadata_via_api
from data_processing import fetch_expanded_metadata

app = Flask(__name__)


@app.route(rule='/', methods=['POST', 'GET'])
def start_menu():
    if request.method == 'POST' and 'search_query' in request.form.keys():
        button = request.form['button']
        search_query = request.form['search_query']
        return search_section(button, search_query)
    return render_template('index.html')


def search_section(button, search_query):
    """Manage the actions and processes for the page search section.

        :param button: str.
        :param search_query: str.
        :return: render_template object.
        """
    if search_query != '' and button == 'validate':
        response = validate_search_query(EXPANDED_APIKEY, search_query)
        if response[0] == 200:
            return render_template(
                'index.html',
                message=f'Records found: {response[1]}',
                search_query=search_query
            )
        return render_template(
            'index.html',
            message=f'Request status: {response[0]}, message: {response[1]}',
            search_query=search_query
        )
    if search_query != '' and button == 'run':
        safe_filename = run_button_main_function(EXPANDED_APIKEY, search_query)
        return render_template('index.html', filename=safe_filename,
            search_query=search_query)
    return render_template('index.html', search_query='')


def run_button_main_function(apikey, search_query):
    """When the 'Run' button is pressed, manage all the API operations,
    data processing, and visualizations

    :param apikey: str.
    :param search_query: str.
    :return: str, tuple.
    """
    records_per_page = 100
    documents_list = []
    initial_json = retrieve_wos_metadata_via_api(apikey, search_query, records_per_page)
    for record in initial_json['Data']['Records']['records']['REC']:
        documents_list.append(fetch_expanded_metadata(record))
    total_results = initial_json['QueryResult']['RecordsFound']
    requests_required = ((total_results - 1) // records_per_page) + 1
    print(f'Total Web of Science API requests required: {requests_required}.')
    for i in range(1, requests_required):
        first_record = int(f'{i}01')
        subsequent_json = retrieve_wos_metadata_via_api(
            apikey,
            search_query,
            records_per_page,
            first_record
        )
        for record in subsequent_json['Data']['Records']['records']['REC']:
            documents_list.append(fetch_expanded_metadata(record))
        print(f'Request {i + 1} of {requests_required} complete.')

    safe_search = search_query.replace('*', '').replace('"', '')
    safe_filename = f'{safe_search} - {date.today()}.txt'

    with open(f'downloads/{safe_filename}', 'w', encoding='UTF8') as writer:
        writer.write('\t'.join([k for k in documents_list[0].keys()]))
        writer.write('\n')
        for doc in documents_list:
            writer.write(f"{'\t'.join([str(v) for v in doc.values()])}\n")

    return f'{safe_filename}'


app.run(debug=True)
