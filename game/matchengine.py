import flask
import os
from azure.cosmosdb.table.tableservice import TableService
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


app = flask.Flask(__name__)

@app.route('/start', methods=['POST'])
def start_round():
    matches = flask.request.get_json()    # requires header content-type of "application/json"
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    keyVault_URI = "https://" + keyVaultName + ".vault.azure.net"

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=keyVault_URI, credential=credential)
    data_access_key = client.get_secret("thecupstore-key")

    table_service = TableService(account_name='thecupstore', account_key=data_access_key.value)

    # Create the query string. Expects a list of matches, each of which is list containing 2 teams.
    query_string = ""
    for match in matches:
        for team in match:
            query_string += "Name eq \'" + team + "\' or "

    # Remove trailing ' or '
    query_string = query_string[:-4]

    global teams
    teams = table_service.query_entities('Teams', filter=query_string)
    return '', 200


@app.route('/play', methods=['GET'])
def play_round():
    pass

if __name__ == "__main__":
    app.run(port=1955, debug=True)