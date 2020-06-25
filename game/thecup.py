# Import statements for third party modules
import flask
import json
import requests
import sys

# Import statements for my modules
import config
import classes.gamestate


app = flask.Flask(__name__)

@app.route('/', methods=['GET'])
def choose_game():
    '''Displays the startup screen, asking player to select the type of game they want'''
    return flask.render_template('choosegame.html')


@app.route('/new', methods=['POST'])
def new_game():
    '''
    POST:
    Depending on the choice, create the storage table.
    Create the right teams from the teams.json.
    Load teams into table.
    Create some information in the table about how many rounds/matches there are.
    Show form, asking them how many teams they want to control, using a checkbox next to each team:
    - for 8 team competition, it's 1
    - for 16 team, it's 1, 2 or 3
    - for 32 team, it's 1, 3, 5
    - for 64 team, it's 1, 4, 5, 10
    Button for submission that checks right number and then submits these teams details to /start.
    '''
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
        print("Error! Exiting")   # this needs some serious work to make it better
        sys.exit()

    # Get the fixture list and enter it into the gamestate object.
    func_resp = requests.post(config.fixture_list_url, data=json.dumps(game_state.get_gameteams()), headers=post_headers)
    if func_resp.status_code !=200:
        print("Error! Exiting")
        sys.exit()
    else:
       game_state.set_fixtures(func_resp.text)
    
    return " ", 222

def show_round_fixtures(details):
    '''
    This should probably record each match/team order in some way so that other parts of the program can output the 
    html in the right order. Maybe output it to another table.
    The other way to do it is to output that as json document.
    This should probably run as a function instead, or a container that basically keeps the fixture list in memory as json
    and allows any other program to query it using REST to get the list.
    Fixtures are worked out at random.
    '''
    pass

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
    app.run(port=1966, debug=True)