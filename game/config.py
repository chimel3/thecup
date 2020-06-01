import json

def get_new_game_app_url():
    data = json.load(open('.\\data_files\\thecupconfig.json'))['config']['new_game_app_url']
    return data

if __name__ == "__main__":
    #ret = get_new_game_app_url()
    #print(ret)
    pass