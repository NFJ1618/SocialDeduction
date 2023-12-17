import random
from game import SecretHitlerGame

class Player:
    
    
    def __init__(self, name, verbose=False):
        self.name = name
        self.role = None
        self.vote = None
        self.chancellor_candidate = None
        self.policy_choice = None
        self.verbose = verbose
        self.trust_rating = {}

    def adjust_trust(self, player_name, adjustment_value):
        """ Adjust the trust value of a player based on new information """
        if player_name not in self.trust_rating:
            self.trust_rating[player_name] = adjustment_value
        else:
            if abs(self.trust_rating[player_name]) < 1000:
                self.trust_rating[player_name] += adjustment_value

    def process_information(self, info_type, involved_players):
        """ Update trust hierarchy based on new information """
        if info_type == SecretHitlerGame.LIBERAL_PASSED:
            for i in involved_players:
                self.adjust_trust(i, 5)
        elif info_type == SecretHitlerGame.FASCIST_PASSED:
            for i in involved_players:
                self.adjust_trust(i, -5)
        elif info_type == SecretHitlerGame.FASCIST_REVEALED:
            for i in involved_players:
                self.adjust_trust(i, -1001)
        elif info_type == SecretHitlerGame.LIBERAL_REVEALED:
            for i in involved_players:
                self.adjust_trust(i, 1001)
            

    def make_decision(self):
        """ Make decisions based on trust hierarchy """
        most_trusted_player = self.trust_hierarchy[0][0] if self.trust_hierarchy else None
        # Depending on the situation, the decision might vary. For now, we return the most trusted player.
        return most_trusted_player

    def assign_role(self, role):
        self.role = role

    def vote_on_government(self, president, potential_chancellor):
        # Implement the logic to let the player make a vote choice here.
        # For simplicity, we'll randomly choose Yes or No.
        self.vote = random.choice([True, False])
        return self.vote

    def choose_chancellor_candidate(self, eligible_candidates):
        # Implement the logic to let the player choose a chancellor candidate here.
        # For simplicity, we'll randomly choose a candidate from the eligible list.
        self.chancellor_candidate = random.choice(eligible_candidates)
        if self.verbose:
            print(f"{self.name} ({self.role}) chooses {self.chancellor_candidate} as the Chancellor candidate.")
        return self.chancellor_candidate

    def choose_policy_to_discard(self, policies_drawn):
        # Implement the logic to let the player choose a policy to discard here.
        # For simplicity, we'll randomly choose a policy from the drawn list.
        discard = random.randint(0,len(policies_drawn)-1)
        discarded = policies_drawn[discard]
        if self.verbose:
            print(f"{self.name} discards {discarded} policy.")
        policies_drawn.remove(discarded)
        return policies_drawn, discarded
    
    def nominate_president_candidate(self, eligible_candidates):
        # Implement the logic to let the player nominate a president candidate here.
        # For simplicity, we'll randomly choose a candidate from the eligible list.
        candidate = random.choice(eligible_candidates)
        if self.verbose:
            print(f"{self.name} nominates {candidate} as the new President candidate.")
        return candidate
    
    def execute_player(self, eligible_candidates):
        eligible_candidates.remove(self.name)
        candidate = random.choice(eligible_candidates)
        if self.verbose:
            print(f"{self.name} executes {candidate}")
        return candidate
    
    
class Liberal(Player):
    def choose_policy_to_discard(self, policies_drawn):
        policies_drawn.sort()
        discard = 0
        discarded = policies_drawn[discard]
        if self.verbose:
            print(f"{self.name} discards {discarded} policy.")
        policies_drawn.remove(discarded)
        return policies_drawn, discarded
    
class Fascist(Player):
    def __init__(self, name, team_mates, hitler, verbose=False):
        super().__init__(name, verbose)
        self.team_mates = team_mates
        self.hitler = hitler
    
    def choose_policy_to_discard(self, policies_drawn):
        policies_drawn.sort(reverse=True)
        discard = 0
        discarded = policies_drawn[discard]
        if self.verbose:
            print(f"{self.name} discards {discarded} policy.")
        policies_drawn.remove(discarded)
        return policies_drawn, discarded
        
class Hitler(Player):
    def choose_policy_to_discard(self, policies_drawn):
        policies_drawn.sort(reverse=True)
        discard = 0
        discarded = policies_drawn[discard]
        if self.verbose:
            print(f"{self.name} discards {discarded} policy.")
        policies_drawn.remove(discarded)
        return policies_drawn, discarded
        