import json

setup_game_url = json.load(open('.\\data_files\\thecupconfig.json'))['config']['new_game_app_url']
teams_controlled_update_url = json.load(open('.\\data_files\\thecupconfig.json'))['config']['teams_controlled_update_url']
fixture_list_url = json.load(open('.\\data_files\\thecupconfig.json'))['config']['fixture_list_url']
match_engine_url = json.load(open('.\\data_files\\thecupconfig.json'))['config']['match_engine_url']
