# Import statements for third party modules
import flask
import json
import requests
import sys
import os
import time
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, TextBase64EncodePolicy, TextBase64DecodePolicy

# Import statements for my modules
import config
import classes.gamestate


app = flask.Flask(__name__)


def create_queue(queue_name, clear_queue):
    credential = DefaultAzureCredential()
    account_url = "https://thecupstore.queue.core.windows.net/"
    queueservice = QueueServiceClient(account_url=account_url, credential=credential)
    try:
        queueservice.create_queue(name=queue_name)
    except:
        # Check that exists and clear if chosen
        if clear_queue:
            for queue in queueservice.list_queues():
                if queue["name"] == queue_name:
                    queue_client = get_queue(queue_name)
                    queue_client.clear_messages()
                    break


def get_queue(queue_name):
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    keyVault_URI = "https://" + keyVaultName + ".vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=keyVault_URI, credential=credential)
    data_access_key = client.get_secret("thecupstore-key")
    account_url = "https://thecupstore.queue.core.windows.net/"
    return QueueClient(account_url=account_url, queue_name=queue_name, credential=data_access_key.value, message_encode_policy=TextBase64EncodePolicy(), message_decode_policy=TextBase64DecodePolicy())


@app.route('/', methods=['GET'])
def choose_game():
    '''Displays the startup screen, asking player to select the type of game they want'''
    return flask.render_template('choosegame.html')


@app.route('/new', methods=['POST'])
def new_game():
    global game_state
    game_state = classes.gamestate.Gamestate(flask.request.form['gametype'])
    # Send game_type to the new game app to load team data. Return value holds teams created, comma delimited
    func_resp = requests.get(config.setup_game_url + '&gametype=' + game_state.get_gametype())
    # Set number of team choices player can make depending on game_type
    if game_state.get_gametype() == "premier":
        game_state.set_num_of_team_choices(["1","3"])
    elif game_state.get_gametype() == "short":
        game_state.set_num_of_team_choices(["1","3","5"])
    elif game_state.get_gametype() == "full":
        game_state.set_num_of_team_choices(["1","3","5","10"])
    else:
        game_state.set_num_of_team_choices(["1"])    # assumes elite but could be some kind of test

    # Load the teams in play into game_state
    game_state.set_gameteams(func_resp.text.split(","))

    # teams should have been passed back in ID order - assuming this is the case here.
    return flask.render_template('chooseteams.html', choices = game_state.get_num_of_team_choices(), teams = game_state.get_gameteams(), usermsg = "")


@app.route('/start', methods=['POST'])
def start_game():
    '''
    Update the teams table to show which teams are player controlled.
    Read table to get round/match details and then call show_round_fixtures(), passing in these details.
    When finished, read the resulted fixture list and output appropriate html with a "Continue" button that simply
    calls a GET on the next /matchday decorator.
    '''
    # temporarily store the user choices to check that they are valid.
    selected_controlled = flask.request.form.get('controlled')
    selected_teams = flask.request.form.getlist('teams')

    if selected_controlled is not None:
        if len(selected_teams) != int(selected_controlled):
            return flask.render_template('chooseteams.html', choices = game_state.get_num_of_team_choices(), teams = game_state.get_gameteams(), usermsg = "Please select the correct number of teams")
    else:
        return flask.render_template('chooseteams.html', choices = game_state.get_num_of_team_choices(), teams = game_state.get_gameteams(), usermsg = "Please select the number of teams to control")
    
    # update the Teams table to record which teams are player controlled
    post_headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    func_resp = requests.post(config.teams_controlled_update_url, data=json.dumps(selected_teams), headers=post_headers)
    if func_resp.status_code != 200:
        print("Error updating player controlled! Exiting: " + str(func_resp.status_code))   # this needs some serious work to make it better
        sys.exit()

    # Get the fixture list and enter it into the gamestate object.
    func_resp = requests.post(config.fixture_list_url, data=json.dumps(game_state.get_gameteams()), headers=post_headers)
    if func_resp.status_code !=200:
        print("Error getting fixture list! Exiting: " + str(func_resp.status_code))
        sys.exit()
    else:
       game_state.set_fixtures(func_resp.text)

    # Update the gamestate object ready to play the round
    game_state.update_matches()
    
    # Create the queues for the matches to run
    create_queue(config.MATCH_TRIGGER_QUEUE, True)
    create_queue(config.GOAL_QUEUE, True)

    # Store the queue object in gamestate to avoid having to continually get it as that takes about 1 second
    game_state.set_goalqueue(get_queue(config.GOAL_QUEUE))

    match_teams, match_scores, timer = game_state.get_matches()
    return flask.render_template('showfixtures.html', teams = match_teams, roundnumber = game_state.get_round())
    

#@app.route('/play', defaults={'tick': None}, methods=['GET'])
#@app.route('/play/<string:tick>', methods=['GET'])
#def play_round(tick):
@app.route('/play', methods=['GET'])
def play_round():
    '''
    This is initially called from the showfixtures page without update (update is None).
    Subsequent calls are made by the matchengine with an update URL filter.
    '''
    print("start of play_round")
    print("1:   " + str(time.time()))
    if game_state.round_has_started():
        # Check for new goal or timer messages
        print("subsequent lap")
        goal_queue = game_state.get_goalqueue()
        if goal_queue.get_queue_properties().approximate_message_count > 0:
            print("2:   " + str(time.time()))
            messages = goal_queue.receive_messages()
            print("3:   " + str(time.time()))
            goals_list = []
            for msg in messages:
                try:
                    int(msg.content)
                except ValueError:
                    goals_list.append(msg.content)
                else:
                    timer = int(msg.content)
                print("4:   " + str(time.time()))
                print("message is: " + str(msg.content))
            print("5:   " + str(time.time()))
            goal_queue.clear_messages()
            print("6:   " + str(time.time()))
            game_state.update_matches(teamlist=goals_list, timer=timer)
            print("7:   " + str(time.time()))
    else:
        # start the round and trigger the match engine
        print("initial lap")
        match_queue = get_queue(config.MATCH_TRIGGER_QUEUE)
        match_queue.send_message(game_state.get_fixturestextstring())
        game_state.round_start()
        
    match_teams, match_scores, timer = game_state.get_matches()
    print(time.time())
    print("timer: " + str(timer))    
    return flask.render_template('showmatches.html', teams = match_teams, scores = match_scores, timer = timer, roundnumber = game_state.get_round())



@app.route('/matchday/', defaults={'trigger': None}, methods=['GET'])
def display_matches():
    '''
    If trigger is None:
    Trigger the process_matches function by putting row in table or txt file on blob store.
    Show the html with all scores set to 0 with an every second refresh automatically.

    If triggered:
    Read the 'scores' queue and 'timer' queue. Suggest don't have any logic about checking the timer value. Just accept it.
    Output the scores as a redrawn HTML page.
    If timer is 90 then finish game (have to think about extra time or replays).
    Need to make sure the "Continue" button is then displayed.
    '''
    pass

def process_matches():
    '''
    This is a function that is woken automatically by something (see display_matches).
    First thing it does is pause for a second or 3 to allow the player to register where their matches are.
    Then process the matches, making sure that each round is processed every second.
    Put name of each team in goalqueue with a single timer event on a timer queue with just the minute number on it.
    Trigger a docker container flask app that has all team names and their scores, starting at 0 in json in memory.
    Docker container reads queue of goals and adds the total to the teams.
    The Docker container possibly then uses a single 'scores' queue that has a single message showing json/yaml/something else
    that python can read.
    This then triggers the /matchday code again.
    '''
    pass

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.run(port=1966, debug=True)