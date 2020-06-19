import logging
import json
import os
import requests

import azure.functions as func
from azure.cosmosdb.table.tableservice import TableService


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    teams = req.params.get('teams')

    if not teams:
        try:
            req_body = req.get_json()
        except ValueError:
            logging.info('Value error retrieving request body')
        else:
            teams = req_body
            logging.info('Request body information retrieved')

        if isinstance(teams, list):
            logging.info('Valid list passed to function in body')
            # get the table details
            accountkey = os.environ["CupstoreKeyId"]
            logging.info('Table storage account key retrieved from key vault')
            accountname = 'thecupstore'
            # connect to the table and update the player controlled teams
            table_service = TableService(account_name=accountname, account_key=accountkey)
            query_string = "Name eq '"
            counter = 1
            for team in teams:
                if counter == len(teams):
                    query_string += team + "'"
                else:
                    query_string += team + "' or Name eq '"
                counter += 1

            logging.info('query string: ' + query_string)
            returned_teams = table_service.query_entities('Teams', filter=query_string)

            for team in returned_teams:
                logging.info('editing team: ' + team.Name)
                team.Controlled = "p1"
                table_service.update_entity('Teams', team)
            
            return func.HttpResponse("", status_code=200)
        else:
            logging.info('Invalid list passed to function in body.')
            return func.HttpResponse("Please provide teams in a list", status_code=422)
    
    else:
        return func.HttpResponse(
             "teams argument invalid",
             status_code=400
        )