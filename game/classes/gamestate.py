
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
            self.gameteams.append(team)

    def get_gameteams(self):
        return self.gameteams
