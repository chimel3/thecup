import logging
import azure.functions as func
import json
import random
from ast import literal_eval


def setup_team_names(file, configs):
    '''Updates the configs array with the teams and their names'''
    contents = file.read()   # class 'bytes'
    decoded_contents = literal_eval(contents.decode('utf-8'))  # class 'str'
    json_contents = json.dumps(decoded_contents, indent=4, sort_keys=True)  # class 'str'
    managed_contents = json.loads(json_contents)  # class 'dict
    l1_teams = managed_contents['teams']['l1'] # hopefully a list
    l2_teams = managed_contents['teams']['l2']
    l3_teams = managed_contents['teams']['l3']
    l4_teams = managed_contents['teams']['l4']
    l5_teams = managed_contents['teams']['l5']
    l6_teams = managed_contents['teams']['l6']

    for config in configs:
        if config["level"] == 1:
            config["name"] = random.choice(l1_teams)      # use this team name in our game
            l1_teams.pop(l1_teams.index(config["name"]))  # remove from the list so we don't reuse the same team

        elif config["level"] == 2:
            config["name"] = random.choice(l2_teams)
            l2_teams.pop(l2_teams.index(config["name"]))

        elif config["level"] == 3:
            config["name"] = random.choice(l3_teams)
            l3_teams.pop(l3_teams.index(config["name"]))

        elif config["level"] == 4:
            config["name"] = random.choice(l4_teams)
            l4_teams.pop(l4_teams.index(config["name"]))

        elif config["level"] == 5:
            config["name"] = random.choice(l5_teams)
            l5_teams.pop(l5_teams.index(config["name"]))

        elif config["level"] == 6:
            config["name"] = random.choice(l6_teams)
            l6_teams.pop(l6_teams.index(config["name"]))

    return configs


def create_team_list(configs):
    '''Creates a simple list of the team names for returning to caller at end'''
    team_names = ""   # initialise as a string
    team_counter = 0  # to count the number of teams to help decide if a comma is needed to separate each one
    for config in configs:
        team_names += config["name"]
        team_counter += 1
        if team_counter < len(configs):
            team_names += ","

    return team_names


def setup_team_values(file, configs):
    '''Updates the configs array with the remaining values'''
    contents = file.read()
    decoded_contents = literal_eval(contents.decode('utf-8'))  # class 'str'
    json_contents = json.dumps(decoded_contents, indent=4, sort_keys=True)  # class 'str'
    managed_contents = json.loads(json_contents)  # class 'dict

    # Set the score and matchscore values
    for config in configs:
        if config["level"] == 1:
            config["score"] = random.randint(managed_contents['scores']['l1']['lowscore'], managed_contents['scores']['l1']['highscore'])
            config["matchscore"] = config["score"]

        elif config["level"] == 2:
            config["score"] = random.randint(managed_contents['scores']['l2']['lowscore'], managed_contents['scores']['l2']['highscore'])
            config["matchscore"] = config["score"]
            
        elif config["level"] == 3:
            config["score"] = random.randint(managed_contents['scores']['l3']['lowscore'], managed_contents['scores']['l3']['highscore'])
            config["matchscore"] = config["score"]
        
        elif config["level"] == 4:
            config["score"] = random.randint(managed_contents['scores']['l4']['lowscore'], managed_contents['scores']['l4']['highscore'])
            config["matchscore"] = config["score"]

        elif config["level"] == 5:
            config["score"] = random.randint(managed_contents['scores']['l5']['lowscore'], managed_contents['scores']['l5']['highscore'])
            config["matchscore"] = config["score"]

        elif config["level"] == 6:
            config["score"] = random.randint(managed_contents['scores']['l6']['lowscore'], managed_contents['scores']['l6']['highscore'])
            config["matchscore"] = config["score"]

        # lookup and set keeperscore
        for keeper_score_index in range(0, 3):
            if managed_contents['keeping'][keeper_score_index]['lowscore'] <= config["score"] <= managed_contents['keeping'][keeper_score_index]['highscore']:
                config["keeperscore"] = managed_contents['keeping'][keeper_score_index]['keepingscore']

    return configs


def add_teams_to_table(teamstable, configs):
    '''Adds the teams and values in the configs array to the table'''
    team_uuid = 0
    output_array = []
    for team in configs:
        team_uuid += 1
        data = {
            "PartitionKey": "thecupteams",
            "RowKey": "t" + str(team_uuid),
            "Name": team["name"],
            "Level": team["level"],
            "Score": team["score"],
            "Match_Score": team["matchscore"],
            "Keeper_Score": team["keeperscore"]
        }
        output_array.append(data)
    
    teamstable.set(json.dumps(output_array))
    

def main(req: func.HttpRequest, teamfile: func.InputStream, valuesfile: func.InputStream, teamstable: func.Out[str]) -> func.HttpResponse:
    '''Checks the gametype passed to the function and then sets up the right number of teams accordingly'''
    gametype = req.params.get('gametype')
    logging.info('Python HTTP trigger. Gametype ' +  gametype)

    if not gametype:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            gametype = req_body.get('gametype')

    team_configs = []   # initialise the array to hold the teams' details

    if gametype == "test":
        # test call. Returns response but does not create anything
        return func.HttpResponse("1", status_code=200)

    elif gametype == "elite":
        # elite games feature the best 8 teams
        for _ in range(0, 6):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for _ in range(0, 2):
            current_config = {"level": 2}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        returned_teams = create_team_list(team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)
        add_teams_to_table(teamstable, team_configs)
        return func.HttpResponse(returned_teams, status_code=200)

    elif gametype == "premier":
        # premier games feature 16 of the best teams
        for _ in range(0, 6):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for _ in range(0, 4):
            current_config = {"level": 2}
            team_configs.append(current_config)

        for _ in range(0, 6):
            current_config = {"level": 3}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        returned_teams = create_team_list(team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)
        add_teams_to_table(teamstable, team_configs)
        return func.HttpResponse(returned_teams, status_code=200)

    elif gametype == "short":
        # short games feature 32 mixed ability teams
        for _ in range(0, 3):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for _ in range(0, 2):
            current_config = {"level": 2}
            team_configs.append(current_config)

        for _ in range(0, 5):
            current_config = {"level": 3}
            team_configs.append(current_config)

        for _ in range(0, 8):
            current_config = {"level": 4}
            team_configs.append(current_config)

        for _ in range(0, 7):
            current_config = {"level": 5}
            team_configs.append(current_config)

        for _ in range(0, 7):
            current_config = {"level": 6}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        returned_teams = create_team_list(team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)
        add_teams_to_table(teamstable, team_configs)
        return func.HttpResponse(returned_teams, status_code=200)

    elif gametype == "full":
        # full games feature all 64 teams
        for _ in range(0, 6):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for _ in range(0, 4):
            current_config = {"level": 2}
            team_configs.append(current_config)

        for _ in range(0, 10):
            current_config = {"level": 3}
            team_configs.append(current_config)

        for _ in range(0, 15):
            current_config = {"level": 4}
            team_configs.append(current_config)

        for _ in range(0, 14):
            current_config = {"level": 5}
            team_configs.append(current_config)

        for _ in range(0, 15):
            current_config = {"level": 6}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        returned_teams = create_team_list(team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)
        add_teams_to_table(teamstable, team_configs)
        return func.HttpResponse(returned_teams, status_code=200)

    else:
        return func.HttpResponse(
             "Invalid gametype",
             status_code=400
        )
