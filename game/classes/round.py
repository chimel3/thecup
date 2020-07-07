import math


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
                            

    @staticmethod
    def _goal_chance_adjustment(score_difference):
        # set limits of score_difference to -10 and +10.
        if score_difference < -10:
            score_difference = -10
        elif score_difference > 10:
            score_difference = 10

        return math.floor(score_difference / -2)   # divides by -2 and then rounds result down