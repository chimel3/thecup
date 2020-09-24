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


def get_queue(queue_name, create_queue, clear_queue):
    ''' Note that generating the queueclient does not mean there must a queue there as one of the properties of queueclient is "create_queue", so it's 
    really a representation of a queue which may or may not exist yet. '''
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    keyVault_URI = "https://" + keyVaultName + ".vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=keyVault_URI, credential=credential)
    data_access_key = client.get_secret("thecupstore-key")
    account_url = "https://thecupstore.queue.core.windows.net/"
    queueclient = QueueClient(account_url=account_url, queue_name=queue_name, credential=data_access_key.value, message_encode_policy=TextBase64EncodePolicy(), message_decode_policy=TextBase64DecodePolicy())
    # Check that the queue exists and if not create it if the create switch has been passed as True
    try:
        queueclient.get_queue_properties()
    except:
        if create_queue:
            queueclient.create_queue()
        else:
            message = "Queue does not exist"
    else:
        if clear_queue:
            queueclient.clear_messages()
    
    if 'message' in locals():   # checks for existence of message variable
        return message
    else:
        return queueclient


def matches_in_progress():
    ''' Cycles through the matches, removing those that are complete and adding the winning team to the next round of fixtures '''
    print("starting matches in progress function")
    round_in_progress = False    # initialises the flag to indicate whether there are still matches that need to be played to conclusion
    match_teams, match_scores, timer = game_state.get_matches()
    print(match_teams)
    print(match_scores)
    # If timer is at 90, then we can call reset_clubs because the fixtures currently held are the ones for the round being played rather than the forthcoming round.
    if timer == 90:
        print("resetting clubs, winning_teams")
        game_state.reset_clubs()
        game_state.clear_winning_teams()
    
    counter = 0
    for team, score in zip(match_teams, match_scores):
        if (counter % 2) == 0:
            print("home team: " + team)
            home_team = team
            home_score = score
        else:
            print("away team: " + team)
            away_team = team
            away_score = score
            print("evaluating match result")
            if home_score > away_score:
                print("home team won")
                game_state.add_winning_team(home_team)
                game_state.remove_match([home_team, away_team])
            elif home_score < away_score:
                print("away team won")
                game_state.add_winning_team(away_team)
                game_state.remove_match([home_team, away_team])
            else:
                # a draw so no winning team
                print("draw")
                round_in_progress = True
        counter += 1

    if not round_in_progress:
        # All matches in the round have concluded. Therefore we can set clubs using the teams we've stored as winning teams
        game_state.add_clubs(game_state.get_winning_teams())

    print("returning " + str(round_in_progress))
    return round_in_progress
    

def create_fixtures():
    # Get the fixture list and enter it into the gamestate object.
    func_resp = requests.post(config.fixture_list_url, data=json.dumps(game_state.get_clubs()), headers=config.post_headers)
    if func_resp.status_code !=200:
        print("Error getting fixture list! Exiting: " + str(func_resp.status_code))
        sys.exit()
    else:
       game_state.set_matches(func_resp.text)
    

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
    game_state.add_clubs(func_resp.text.split(","))

    # teams should have been passed back in ID order - assuming this is the case here.
    return flask.render_template('chooseteams.html', choices = game_state.get_num_of_team_choices(), teams = game_state.get_clubs(), usermsg = "")


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
            return flask.render_template('chooseteams.html', choices = game_state.get_num_of_team_choices(), teams = game_state.get_clubs(), usermsg = "Please select the correct number of teams")
    else:
        return flask.render_template('chooseteams.html', choices = game_state.get_num_of_team_choices(), teams = game_state.get_clubs(), usermsg = "Please select the number of teams to control")
    
    # update the Teams table to record which teams are player controlled
    func_resp = requests.post(config.teams_controlled_update_url, data=json.dumps(selected_teams), headers=config.post_headers)
    if func_resp.status_code != 200:
        print("Error updating player controlled! Exiting: " + str(func_resp.status_code))   # this needs some serious work to make it better
        sys.exit()
    
    # Attempt to create queues. Try 3 times to handle error I've seen when for some reason Azure doesn't create a queue for some reason.
    matchtrigger_queue = get_queue(config.MATCH_TRIGGER_QUEUE, True, True)
    time.sleep(0.1)
    func_resp = get_queue(config.MATCH_TRIGGER_QUEUE, False, False)
    counter = 0
    while func_resp == "Queue does not exist":
        if counter <= 1:
            matchtrigger_queue = get_queue(config.MATCH_TRIGGER_QUEUE, True, True)
            time.sleep(0.1)
            func_resp = get_queue(config.MATCH_TRIGGER_QUEUE, False, False)
            counter += 1
        else:
            raise RuntimeError(config.MATCH_TRIGGER_QUEUE + "cannot be created.")

    game_state.set_matchqueue(matchtrigger_queue)  # Store the queue objects in gamestate to avoid having to continually get it as that takes about 1 second

    goal_queue = get_queue(config.GOAL_QUEUE, True, True)
    time.sleep(0.1)
    func_resp = get_queue(config.GOAL_QUEUE, False, False)
    counter = 0
    while func_resp == "Queue does not exist":
        if counter <= 1:
            matchtrigger_queue = get_queue(config.GOAL_QUEUE, True, True)
            time.sleep(0.1)
            func_resp = get_queue(config.GOAL_QUEUE, False, False)
            counter += 1
        else:
            raise RuntimeError(config.MATCH_TRIGGER_QUEUE + "cannot be created.")

    game_state.set_goalqueue(goal_queue)  # Store the queue objects in gamestate to avoid having to continually get it as that takes about 1 second
    
    create_fixtures()
    game_state.set_round_status("notstarted")
    match_teams, match_scores, timer = game_state.get_matches()
    return flask.render_template('showfixtures.html', teams = match_teams, roundnumber = game_state.get_round())
    

@app.route('/play', methods=['GET'])
def play_round():
    if game_state.get_round_status() == "inplay":
        # Check for new goal or timer messages
        goal_queue = game_state.get_goalqueue()
        if goal_queue.get_queue_properties().approximate_message_count > 0:
            messages = goal_queue.receive_messages()
            goals_list = []
            for msg in messages:
                try:
                    int(msg.content)
                except ValueError:
                    if msg.content == "done":    # this will be used to indicate the end of penalties or a round of sudden death penalties
                        print("done message received")
                        game_state.set_round_status("paused")
                        timer = ""
                    else:
                        goals_list.append(msg.content)
                else:
                    timer = int(msg.content)
                    print("timer: " + str(timer))
            goal_queue.clear_messages()
            game_state.update_matches(teamlist=goals_list, timer=timer)
        game_state.set_match_message("")
        screen_url = "play_round"
    
    elif game_state.get_round_status() == "notstarted":
        print("notstarted")
        game_state.set_engine_message("normal")
        game_state.set_match_message("Ready")
        game_state.set_round_status("ready")
        screen_url = "play_round"

    elif game_state.get_round_status() == "ready":
        print("ready")
        match_queue = game_state.get_matchqueue()
        match_queue.send_message(game_state.get_engine_message() + ',' + game_state.get_fixturestextstring())
        print("fixturetextstring: " + game_state.get_fixturestextstring())
        game_state.set_round_status("inplay")
        game_state.set_match_message("")
        screen_url = "play_round"

    elif game_state.get_round_status() == "paused":
        print("paused")
        if matches_in_progress():
            #print("matches are in progress")
            if game_state.get_timer() == 90:
                print("timer is 90 so sending extra msg")
                game_state.set_engine_message("extra")
                game_state.set_match_message("Extra Time")
            elif game_state.get_timer() == 120:
                # Check to see if we have already had penalties and are in sudden death, or not
                if game_state.get_match_message() == "":
                    game_state.set_engine_message("penalties")
                    game_state.set_match_message("Penalties!")
                else:
                    game_state.set_engine_message("suddendeath")
                    game_state.set_match_message("Sudden death penalties!")
            game_state.set_round_status("ready")
            screen_url = "play_round"
        else:
            print("no matches in progress still")
            game_state.set_round_status("finished")
            game_state.set_match_message("Round Complete")
            screen_url = "next_round"
        
    match_teams, match_scores, timer = game_state.get_matches()
    return flask.render_template('showmatches.html', teams = match_teams, scores = match_scores, timer = timer, roundnumber = game_state.get_round(), status = game_state.get_round_status(), matchmsg = game_state.get_match_message(), destination = screen_url)


@app.route('/next', methods=['GET'])
def next_round():
    return '', 200


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.run(port=1966, debug=True)