import logging
import azure.functions as func
import json
import random
from ast import literal_eval

def setup_team_names(file, configs):
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


def setup_team_values(file, configs):
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


def main(req: func.HttpRequest, teamfile: func.InputStream, valuesfile: func.InputStream, teamdetails: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    gametype = req.params.get('gametype')
    if not gametype:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            gametype = req_body.get('gametype')

    
    #team_data = teamfile.read()  # class 'bytes'
    #values_data = valuesfile.read()
    team_configs = []

    if gametype == "elite":
        # elite games feature the best 8 teams
        for each_team in range(0, 6):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for each_team in range(0, 2):
            current_config = {"level": 2}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)

    elif gametype == "premier":
        # premier games feature 16 of the best teams
        for each_team in range(0, 6):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for each_team in range(0, 4):
            current_config = {"level": 2}
            team_configs.append(current_config)

        for each_team in range(0, 6):
            current_config = {"level": 3}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)

    elif gametype == "short":
        # short games feature 32 mixed ability teams
        for each_team in range(0, 3):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for each_team in range(0, 2):
            current_config = {"level": 2}
            team_configs.append(current_config)

        for each_team in range(0, 5):
            current_config = {"level": 3}
            team_configs.append(current_config)

        for each_team in range(0, 8):
            current_config = {"level": 4}
            team_configs.append(current_config)

        for each_team in range(0, 7):
            current_config = {"level": 5}
            team_configs.append(current_config)

        for each_team in range(0, 7):
            current_config = {"level": 6}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)

    elif gametype == "full":
        # full games feature all 64 teams
        for each_team in range(0, 6):
            current_config = {"level": 1}
            team_configs.append(current_config)

        for each_team in range(0, 4):
            current_config = {"level": 2}
            team_configs.append(current_config)

        for each_team in range(0, 10):
            current_config = {"level": 3}
            team_configs.append(current_config)

        for each_team in range(0, 15):
            current_config = {"level": 4}
            team_configs.append(current_config)

        for each_team in range(0, 14):
            current_config = {"level": 5}
            team_configs.append(current_config)

        for each_team in range(0, 15):
            current_config = {"level": 6}
            team_configs.append(current_config)

        team_configs = setup_team_names(teamfile, team_configs)
        team_configs = setup_team_values(valuesfile, team_configs)

        ##team_data = teamfile.read()  # class 'bytes'
        #jsondata = json.loads(team_data)
        ##outputdatastr = literal_eval(team_data.decode('utf-8'))  # class 'str' - convert to string
        #outputdataf = json.dumps(outputdatastr)   # class 'str'
        #outputdatad = json.loads(outputdatastr)
        ##outputdataf = json.dumps(outputdatastr, indent=4, sort_keys=True)  # class 'str'
        #output1 = outputdatastr['teams']['l1']
        ##t1 = json.loads(outputdataf)  # class 'dict
        ##t2 = t1['teams']['l1']  # class 'dict'
        

        return func.HttpResponse(str(t2))

        '''
        data = {
            "PartitionKey": "thecupteams",
            "RowKey": "T3",
            "Name": "Arsenal",
            "Level": "l1",
            "Score": 0,
            "Match_Score": 0,
            "Keeper_Score": 0
        }
        teamdetails.set(json.dumps(data))
        return func.HttpResponse(f"Hello {gametype}!")
        '''
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )

