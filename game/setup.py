import logging
import azure.functions as func
import json


def main(req: func.HttpRequest, details: func.Out[str]) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    gametype = req.params.get('gametype')
    if not gametype:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            gametype = req_body.get('gametype')

    if gametype:
        '''
        data = {
            "PartitionKey": "thecup",
            "RowKey": "T2",
            "Name": "Liverpool",
            "Level": "l1",
            "Score": 0,
            "Match_Score": 0,
            "Keeper_Score": 0
        }
        details.set(json.dumps(data))'''
        return func.HttpResponse(f"Hello {gametype}!")
    else:
        return func.HttpResponse(
             "Please pass a name on the query string or in the request body",
             status_code=400
        )
