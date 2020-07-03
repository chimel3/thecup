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
    teams = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twentyone", "twentytwo", "twentythree", "twentyfour", "twentyfive", "twentysix", "twentyseven", "twentyeight", "twentynine", "thirty", "thirtyone", "thirtytwo", "thirtythree", "thirtyfour", "thirtyfive", "thirtysix", "thirtyseven", "thirtyeight", "thirtynine", "forty", "fortyone", "fortytwo", "fortythree", "fortyfour", "fortyfive", "fortysix", "fortyseven", "fortyeight", "fortynine", "fifty", "fiftyone", "fiftytwo", "fiftythree", "fiftyfour", "fiftyfive", "fiftysix", "fiftyseven", "fiftyeight", "fiftynine", "sixty", "sixtyone", "sixtytwo", "sixtythree", "sixtyfour"]
    scores = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39", "40", "41", "42", "43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53", "54", "55", "56", "57", "58", "59", "60", "61", "62", "63", "64"]
    return flask.render_template('showmatches.html', teams=teams, scores=scores, roundnumber="Quarter Finals")

@app.route('/new', methods=['POST'])
def start_game():
    print("done")
    return "", 222

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.run(port=1967, debug=True)