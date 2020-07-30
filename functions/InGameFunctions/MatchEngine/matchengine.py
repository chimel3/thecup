import logging
import base64
import math
import random
import os
import time
import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage, TextBase64EncodePolicy


class Round():
    '''Creates a round object that is used to store details of the teams involved in the current round of matches.
    By being stored in the same order as the fixture list it allows me to enumerate through the matches to see
    whether a goal is scored by either team involved in a match without having to constantly try and find the 
    stats for the team in the dataset output from reading the table data
    '''
    # Static properties
    DEFAULT_GOAL_CHANCE = 86   # this is the default value that a team must score in order to create a goal chance.
    
    def __init__(self, matches, stats):
        self.matches = []
        for match in matches:
            hometeam = {"name": match[0]}
            awayteam = {"name": match[1]}

            for team_details in stats:
                # Note: it seems to be that Int32 value types in the table need to be accessed using the "value" property
                if hometeam["name"] == team_details.Name:
                    hometeam["score"] = team_details.Match_Score.value
                    hometeam["keeping"] = team_details.Keeper_Score.value
                if awayteam["name"] == team_details.Name:
                    awayteam["score"] = team_details.Match_Score.value
                    awayteam["keeping"] = team_details.Keeper_Score.value
                
            # Calculate the adjusted GOAL_CHANCE value
            hometeam["goal_chance"] = Round.DEFAULT_GOAL_CHANCE + (self._goal_chance_adjustment(hometeam["score"] - awayteam["score"]))
            awayteam["goal_chance"] = Round.DEFAULT_GOAL_CHANCE + (self._goal_chance_adjustment(awayteam["score"] - hometeam["score"]))

            self.matches.append([hometeam, awayteam])


    def get_matches(self):
        return self.matches
                            

    @staticmethod
    def _goal_chance_adjustment(score_difference):
        # set limits of score_difference to -10 and +10.
        if score_difference < -10:
            score_difference = -10
        elif score_difference > 10:
            score_difference = 10

        return math.floor(score_difference / -2)   # divides by -2 and then rounds result down


def create_fixtures(teamlist):
    ''' Takes a list of teams and returns a fixture list (list of lists) '''
    fixtures = []
    current_match = []
    for team in teamlist:
        if len(current_match) == 0:
            current_match = [team]
        else:
            current_match.append(team)
            fixtures.append(current_match)
            current_match = []
    return fixtures
    

def goal_chance(target_score):
    ''' Takes the current goal chance value of the team and works out if it has been hit '''
    NUM_DICE = 12
    NUM_SIDES = 10

    total_score = 0
    for dice in range(NUM_DICE):
        total_score += random.randint(1, NUM_SIDES)

    if total_score >= target_score:
        return True
    else:
        return False

    
def goal_saved(keeper_score):
    if random.randint(1, 100) <= keeper_score:
        return True
    else:
        return False


def main(trigger: func.QueueMessage):
    '''
    The function has to use imported code libraries to write to the queue because otherwise writes are 
    only done when the function has finished.
    '''
    logging.info('matchengine triggered')
    message = trigger.get_body().decode()  # to decode to utf-8 and remove leading b' 
    
    # The message coming in has to be just text for base 64 decoding, so expect a string of team names in fixture list order. 
    team_list = message.split(",")
    query_string = ""
    for team in team_list:
        query_string += "Name eq \'" + team + "\' or "
    query_string = query_string[:-4]    # Remove trailing ' or '

    # Get the team stats from the table
    keyVaultName = os.environ["KEY_VAULT_NAME"]
    keyVault_URI = "https://" + keyVaultName + ".vault.azure.net"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=keyVault_URI, credential=credential)
    data_access_key = client.get_secret("thecupstore-key")

    table_service = TableService(account_name='thecupstore', account_key=data_access_key.value)
    team_stats = table_service.query_entities('Teams', filter=query_string)

    # Set up the queue to write goals and timer intervals to
    account_url = "https://thecupstore.queue.core.windows.net/"
    queue_name = "goalqueue"
    goal_queue = QueueClient(account_url=account_url, queue_name=queue_name, credential=data_access_key.value, message_encode_policy=TextBase64EncodePolicy())

    # Get in fixture list format and create the current round ready to play
    fixtures = create_fixtures(team_list)
    current_round = Round(fixtures, team_stats)
    matches = current_round.get_matches()
    MATCH_LENGTH = 90
    match_time = 0
    while match_time <= MATCH_LENGTH:
        for match in matches:
            for team in match:
                if goal_chance(team["goal_chance"]):
                    # goal chance created. Check if saved.
                    if goal_saved(team["keeping"]):
                        pass
                    else:
                        # goal scored
                        goal_queue.send_message(team["name"])

        logging.info('writing timer to queue ' + str(match_time))
        goal_queue.send_message(str(match_time))
        # Check if the goalqueue is clear before continuing. This is to keep the matchengine in sync with the user form. This way they should see a smooth
        # progression of the timer. Without this check matchengine tends to run fast and multiple second jumps are observed.
        while goal_queue.get_queue_properties().approximate_message_count > 0:
            time.sleep(0.05)            

        match_time += 1
    logging.info('matchengine complete')



