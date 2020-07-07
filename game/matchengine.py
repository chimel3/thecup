import flask
import os
import time
import random
from azure.cosmosdb.table.tableservice import TableService
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

import classes.round


def goal_chance(target_score):
    ''' Takes the current goal chance value of the team and works out if it has been hit '''
    NUM_DICE = 12
    NUM_SIDES = 10

    total_score = 0
    for dice in range(NUM_DICE):
        total_score += random.randint(1, 10)

    print("target score: " + target_score + "   total_score:" + total_score)
    if total_score >= target_score:
        return True
    else:
        return False

    
def goal_saved(keeper_score):
    if random.randint(1, 100) <= keeper_score:
        return True
    else:
        return False


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

    team_stats = table_service.query_entities('Teams', filter=query_string)
    global match_details
    match_details = classes.round.Round(matches, team_stats)
    return '', 200


@app.route('/play', methods=['GET'])
def play_round():
    match_time = 0
    while match_time < 5:
        start_time = time.time()
        for match in match_details:
            for team in match:
                if goal_chance(team["goal_chance"]):
                    # goal chance created. Check if saved.
                    if goal_saved(team["keeping"]):
                        print("saved: " + team["Name"])
                    else:
                        # goal scored
                        print("goal: " + team["Name"])

        # Check if a second has passed. Otherwise wait until it has
        while time.time() < start_time + 1:
            # Rather than have a busy wait using "pass" we will sleep for a short period of time before looping again
            time.sleep(0.05)

        match_time += 1

        


if __name__ == "__main__":
    app.run(port=1955, debug=True)