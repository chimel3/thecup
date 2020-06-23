import flask
from flask import jsonify, request, abort
import json


app = flask.Flask(__name__)

def validate_teams(data):
    '''Makes some basic checks of the data before creating the fixture list'''
    if isinstance(data, list):
        if len(data) % 2 == 0:
            return True
        else:
            return False
    else:
        return False


@app.route('/all', methods=['GET', 'POST'])
def fixtures():
    if flask.request.method == 'GET':
        pass
    else:
        # POST request - we are being given a new list of teams to generate fixtures
        post_data = request.get_json()  # requires a header of content type "application/json" or won't think it is json
        if validate_teams:
            return '', 200
        else:
            return '', 400

if __name__ == "__main__":
    app.run(port=1955, debug=True)