import logging
import random
import azure.functions as func


def valid_data(data):
    '''Makes some basic checks of the data before creating the fixture list'''
    if isinstance(data, list):
        if len(data) % 2 == 0:
            return True
        else:
            return False
    else:
        return False


def draw_team(teams):
    drawn_team = random.choice(teams)
    teams.pop(teams.index(drawn_team))
    return drawn_team


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        req_body = req.get_json()
    except ValueError:
        logging.info('Value error retrieving request body')
    else:
        teams = req_body
        logging.info('Request body information retrieved')

    if valid_data(teams):
        fixtures = draw_team(teams) + ','
        while len(teams) > 1:
            fixtures += (draw_team(teams) + ',')
        
        # should now be just 1 team left in list
        fixtures += draw_team(teams)
        return func.HttpResponse(fixtures, status_code=200)
    else:
        logging.info('Invalid data received')
        return func.HttpResponse(
             "Data failed validity checks. Please check that it is a list with even number of teams",
             status_code=422
        )
