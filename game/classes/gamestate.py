
class Gamestate():
    '''Creates a gamestate object that is used to store various bits of information that are required across functions'''
    
    def __init__(self, gametype):
        self.gametype = gametype
        self.choices = []
        self.gameteams = []

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

    def get_single_fixture(self, match_number):
        return self.fixtures[match_number - 1]

    def get_round():
        return self.tournament_round