
class Gamestate():
    '''Creates a gamestate object that is used to store various bits of information that are required across functions'''
    
    def __init__(self, gametype):
        self.gametype = gametype
        self.choices = []
        self.gameteams = []
        self.round_started = False

    def get_gametype(self):
        return self.gametype
    
    def set_num_of_team_choices(self, choices):
        self.choices = choices

    def get_num_of_team_choices(self):
        return self.choices

    def set_gameteams(self, teams):
        for team in teams:
            #print("team set in gamestate: " + team)
            self.gameteams.append(team)

    def get_gameteams(self):
        return self.gameteams

    def set_fixtures(self, teams):
        self.fixturetextstring = teams
        working_list = teams.split(",")
        self.fixtures = []
        current_match = []
        for team in working_list:
            if len(current_match) == 0:
                current_match = [team]
            else:
                current_match.append(team)
                self.fixtures.append(current_match)
                current_match = []   # initially tried current_match.clear() but this also cleared self.fixtures due to the by reference value assignment of Python

        # Evaluate the tournament round based on number of teams remaining
        if len(working_list) == 2:
            self.tournament_round = 'Final'
        elif len(working_list) == 4:
            self.tournament_round = 'Semi Finals'
        elif len(working_list) == 8:
            self.tournament_round = 'Quarter Finals'
        elif len(working_list) == 16:
            if self.gametype == 'premier':
                self.tournament_round = 'First Round'
            elif self.gametype == 'short':
                self.tournament_round = 'Second Round'
            else:
                self.tournament_round = 'Third Round'
        elif len(working_list) == 32:
            if self.gametype == 'short':
                self.tournament_round = 'First Round'
            else:
                self.tournament_round = 'Second Round'
        else:
            self.tournament_round = 'First Round' 

    def get_fixtures(self):
        return self.fixtures

    def get_fixturestextstring(self):
        return self.fixturetextstring

    def get_single_fixture(self, match_number):
        return self.fixtures[match_number - 1]

    def get_round(self):
        return self.tournament_round

    def update_matches(self, teamlist=None, timer=None):
        ''' Updates the scores for the matches or sets them up if no teamlist parameter is passed in.
        The teamlist parameter is a single dimension list in fixture list order
        '''
        if teamlist is not None:
            # Find the team name in match_teams and update the equivalent item number in the match_scores list.
            for team_name in teamlist:
                self.match_scores[self.match_teams.index(team_name)] += 1
            self.timer = timer
        else:
            # Convert the fixtures list of lists to a flat list for use in the output html in the matches
            self.match_teams = [item for sublist in self.get_fixtures() for item in sublist]
            # Create the scores list with the same number of elements
            self.match_scores = []
            for _ in range(0, len(self.match_teams)):
                self.match_scores.append(0)
            self.timer = 0

    def get_matches(self):
        ''' Returns 2 single dimension lists in fixture list order '''
        return self.match_teams, self.match_scores, self.timer

    def set_goalqueue(self, queueclient):
        '''Stores the queueclient object '''
        self.goalqueue = queueclient

    def get_goalqueue(self):
        return self.goalqueue

    def round_start(self):
        self.round_started = True

    def round_stop(self):
        self.round_started = False

    def round_has_started(self):
        return self.round_started
