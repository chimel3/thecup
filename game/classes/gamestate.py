class Gamestate():
    '''Creates a gamestate object that is used to store various bits of information that are required across functions'''
    
    def __init__(self, gametype):
        self.gametype = gametype
        self.choices = []
        self.clubs = []
        self.round_started = False
        self.winningteams = []


    ### General game settings ###
    def get_gametype(self):
        return self.gametype
    

    def set_num_of_team_choices(self, choices):
        self.choices = choices


    def get_num_of_team_choices(self):
        return self.choices
    ### End section ###


    ### Adds, gets and resets the clubs that are still in the game ###
    def add_clubs(self, clubs):
        for club in clubs:
            self.clubs.append(club)


    def get_clubs(self):
        return self.clubs


    def reset_clubs(self):
        self.clubs.clear() 
    ### End section ###


    ### Match processing ###
    def get_round(self):
        return self.tournament_round


    def set_matches(self, teams):
        self.matches = teams.split(",")
        self.scores = []
        for _ in range(0, len(self.matches)):
            self.scores.append(0)
        self.timer = 0
        self.round_started = False
        
        # Evaluate the tournament round based on number of teams remaining
        if len(self.matches) == 2:
            self.tournament_round = 'Final'
        elif len(self.matches) == 4:
            self.tournament_round = 'Semi Finals'
        elif len(self.matches) == 8:
            self.tournament_round = 'Quarter Finals'
        elif len(self.matches) == 16:
            if self.gametype == 'premier':
                self.tournament_round = 'First Round'
            elif self.gametype == 'short':
                self.tournament_round = 'Second Round'
            else:
                self.tournament_round = 'Third Round'
        elif len(self.matches) == 32:
            if self.gametype == 'short':
                self.tournament_round = 'First Round'
            else:
                self.tournament_round = 'Second Round'
        else:
            self.tournament_round = 'First Round' 


    def get_fixturestextstring(self):
        glue = ","
        fixturetextstring = glue.join(self.matches)
        return fixturetextstring


    def update_matches(self, teamlist=None, timer=None):
        ''' Updates the scores for the matches or sets them up if no teamlist parameter is passed in.
        The teamlist parameter is a single dimension list in fixture list order
        '''
        if teamlist is not None:
            # Find the team name in match_teams and update the equivalent item number in the match_scores list.
            for team_name in teamlist:
                self.scores[self.matches.index(team_name)] += 1
            self.timer = timer
            if timer == 90 or timer == 120:
                if self.round_status != "paused":
                    self.set_round_status("paused")


    def remove_match(self, teams):
        ''' teams will be a list of the home team followed by away team that will be removed ["hometeam", "awayteam"] '''
        print("removing match featuring the teams:")
        for team in teams:
            print(team)
            index_value = self.matches.index(team)
            self.matches.pop(index_value)
            self.scores.pop(index_value)


    def get_matches(self):
        ''' Returns 2 single dimension lists in fixture list order. Lists passed as copies rather than references so can be modified outside without affecting the class. '''
        return self.matches.copy(), self.scores.copy(), self.timer


    def get_timer(self):
        return self.timer
    ### End section ###


    ### Queue storage ###
    def set_goalqueue(self, queueclient):
        '''Stores the queueclient object '''
        self.goalqueue = queueclient

    def get_goalqueue(self):
        return self.goalqueue

    def set_matchqueue(self, queueclient):
        self.matchqueue = queueclient

    def get_matchqueue(self):
        return self.matchqueue
    ### End section ###


    ### Status of current round in play ###
    def set_round_status(self, status):
        self.round_status = status

    def get_round_status(self):
        return self.round_status
    ### End section ###


    ### Match message ###
    def set_match_message(self, message):
        self.match_message = message
    
    def get_match_message(self):
        return self.match_message
    ### End section ###


    ### Processing winning teams ###
    def add_winning_team(self, team):
        # single team to be passed as a string
        self.winningteams.append(team)

    def get_winning_teams(self):
        return self.winningteams

    def clear_winning_teams(self):
        self.winningteams.clear()
    ### End section ###


    ### Matchengine message ###
    def set_engine_message(self, message):
        self.engine_message = message

    def get_engine_message(self):
        return self.engine_message
    ### End section ###