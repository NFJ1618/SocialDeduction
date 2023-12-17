import random
import itertools
from player import *

class SecretHitlerGame:
    POLICY = "Policy"
    LIBERAL_PASSED = "Liberal Passed"
    FASCIST_PASSED = "Fascist Passed"
    LIBERAL_REVEALED = "Liberal Revealed"
    FASCIST_REVEALED = "Fascist Revealed"
    
    
    
    distribution = {
            5: {'Liberal': 3, 'Fascist': 1, 'Hitler': 1},
            6: {'Liberal': 4, 'Fascist': 1, 'Hitler': 1},
            7: {'Liberal': 4, 'Fascist': 2, 'Hitler': 1},
            8: {'Liberal': 5, 'Fascist': 2, 'Hitler': 1},
            9: {'Liberal': 5, 'Fascist': 3, 'Hitler': 1},
            10: {'Liberal': 6, 'Fascist': 3, 'Hitler': 1}
        }
    
    tracks = {
        5: {
            6: 'None',
            5: "Execute+Veto",
            4: "Execute",
            3: "Policy Peek",
            2: "None",
            1: "None"
        },
        6: {
            6: 'None',
            5: "Execute+Veto",
            4: "Execute",
            3: "Policy Peek",
            2: "None",
            1: "None"
        },
        7: {
            6: 'None',
            5: "Execute+Veto",
            4: "Execute",
            3: "Special Election",
            2: "Investigate",
            1: "None"
        },
        8: {
            6: 'None',
            5: "Execute+Veto",
            4: "Execute",
            3: "Special Election",
            2: "Investigate",
            1: "None"    
        },
        9: {
            6: 'None',
            5: "Execute+Veto",
            4: "Execute",
            3: "Special Election",
            2: "Investigate",
            1: "Investigate"    
        },
        10: {            
            6: 'None',
            5: "Execute+Veto",
            4: "Execute",
            3: "Special Election",
            2: "Investigate",
            1: "Investigate"
        }
    }
    
    def __init__(self, num_players, verbose=False):
        self.end_state = None
        self.verbose = verbose
        self.num_players = num_players
        self.constructor_map = {'Liberal': Liberal, 'Fascist': Fascist, 'Hitler': Hitler}
        self.player_types = ['Liberal', 'Fascist', 'Hitler']
        self.constructors = []
        for k, v in SecretHitlerGame.distribution[num_players].items():
            self.constructors.extend([self.constructor_map[k] for i in range(v)])
        random.shuffle(self.constructors)
        self.players = [f"Player {i+1}" for i in range(num_players)]
        self.alive_players = self.players[:]
        self.player_map = {name: self.constructors[ind](name, self.verbose) for ind, name in enumerate(self.players)}
        self.roles = []
        self.policy_deck = ['Liberal'] * 6 + ['Fascist'] * 11
        self.discarded = []
        self.board_state = {
            'liberal_policies': 0,
            'fascist_policies': 0,
            'election_tracker': 0,
            'president': len(self.alive_players),
            'chancellor': None,
        }
        
        self.game_state = {
            'liberal_policies': 0,
            'fascist_policies': 0,
            'election_tracker': 0,
            'president': len(self.alive_players),
            'chancellor': None,
            
            "term_limited": [],
            "event_bus": []
        }
        
        self.term_limited = []
        self.event_bus = []
        self.temp_president = None
        self.next_president = None
        self.president_ptr = None
        self.chancellor_ptr = None
        self.fascist_track = SecretHitlerGame.tracks[num_players]
        self.executed_players = 0
        self.hitler_elected = False
        self.game_over = False
        self.hitler_executed = False

    def shuffle_roles(self):
        roles = [[i] * (self.distribution[self.num_players][i]) for i in self.player_types]
        roles = sum(roles, [])
        random.shuffle(roles)
        self.roles = roles

    def draw_policy(self):
        return self.policy_deck.pop()

    def enact_policy(self, policy):
        if policy == 'Liberal':
            self.board_state['liberal_policies'] += 1
        elif policy == 'Fascist':
            self.board_state['fascist_policies'] += 1
            self.execute_fascist_power(self.fascist_track[self.board_state['fascist_policies']])

    def get_next_president(self, current_president):
        ind = self.alive_players.index(current_president) + 1
        if ind >= len(self.alive_players):
            return 0
        return ind
        

    def elect_government(self):
        eligible_players = [player for player in self.alive_players]
        if self.temp_president is None:
            president_name = self.alive_players[self.get_next_president(self.president_ptr.name)] if self.president_ptr is not None else self.alive_players[0]
        else:
            if self.next_president is None:
                self.next_president = self.alive_players[self.get_next_president(self.president_ptr.name)]
                president_name = self.temp_president
                self.temp_president = None
            else:
                president_name = self.next_president
                self.next_president = None

        president = self.player_map[president_name]
        eligible_players.remove(president_name)
        
        for p in self.term_limited:
            try:
                eligible_players.remove(p)
            except ValueError:
                pass
        
        potential_chancellor_name = president.choose_chancellor_candidate(eligible_players)
        return president_name, potential_chancellor_name

    def vote_on_government(self, president, potential_chancellor):
        votes = [self.player_map[player].vote_on_government(president, potential_chancellor) for player in self.players]
        num_yes_votes = sum(votes)
        num_no_votes = len(votes) - num_yes_votes
        if self.verbose:
            print(f"Votes: Yes - {num_yes_votes}, No - {num_no_votes}")

        if num_yes_votes > num_no_votes:
            if self.verbose:
                print("Government elected!")
            self.president_ptr = self.player_map[president]
            self.chancellor_ptr = self.player_map[potential_chancellor]
            self.term_limited = [self.president_ptr.name, self.chancellor_ptr.name]
            if self.board_state['fascist_policies'] >= 3:
                if self.chancellor_ptr.role == 'Hitler':
                    self.hitler_elected = True
            return True
        else:
            if self.verbose:
                print("Government rejected!")
            return False

    def investigate(self, role):
        if role == 'Hitler':
            return 'Fascist'
        return role

    def policy_phase(self):
        policies_drawn = [self.draw_policy() for _ in range(3)]
        if self.verbose:
            print(f"Policies drawn: {policies_drawn}")
        
        remaining, discarded = self.president_ptr.choose_policy_to_discard(policies_drawn)
        self.discarded.append(discarded)
        
        remaining, discarded = self.chancellor_ptr.choose_policy_to_discard(remaining)
        self.discarded.append(discarded)

        self.enact_policy(remaining[0])
        if len(self.policy_deck) < 3:
            self.policy_deck.extend(self.discarded)
            self.discarded = []
            random.shuffle(self.policy_deck)

    def execute_fascist_power(self, power):
        if power == 'Investigate':
            # do nothing for now
            return
            player = random.choice([p for p in self.alive_players if p != self.board_state['president']])
            role = self.roles[self.players.index(player)]
            if self.verbose:
                print(f"{self.board_state['president']} investigates the loyalty of {player}. Result: {self.investigate(role)}")
        elif power == 'Policy Peek':
            # do nothing for now
            return
            policies_peeked = [self.draw_policy() for _ in range(3)]
            if self.verbose:
                print(f"{self.board_state['president']} peeks at the next 3 policies: {policies_peeked}")
        elif power.startswith("Execute"):
            eligible_players = [p for p in self.alive_players]
            player_to_execute = self.president_ptr.execute_player(eligible_players)
            self.alive_players.remove(player_to_execute)
            role = self.player_map[player_to_execute].role
            if self.verbose:
                print(f"{self.board_state['president']} executes {player_to_execute}. Result: {role}")
            if role == 'Hitler':
                self.hitler_executed = True
        elif power == 'Special Election':
            eligible_players = [p for p in self.alive_players if p != self.board_state['president']]
            new_president = self.president_ptr.nominate_president_candidate(eligible_players)
            self.temp_president = new_president
            if self.verbose:
                print(f"{self.board_state['president']} calls for a special election and nominates {new_president}.")
        else:
            pass

    def start_game(self):
        self.shuffle_roles()
        random.shuffle(self.players)
        self.alive_players = self.players[:]
        for player, role in zip(self.players, self.roles):
            self.player_map[player].assign_role(role)
            if self.verbose:
                print(f"{player} - {role}")

    def run_game_simulation(self):
        self.start_game()

        while not self.game_over:
            if self.board_state['liberal_policies'] == 5:
                if self.verbose:
                    print("Liberals Win!")
                self.game_over = True
                self.end_state = 0
                break
            elif self.board_state['fascist_policies'] == 6:
                if self.verbose:
                    print("Fascists Win!")
                self.game_over = True
                self.end_state = 1
                break

            president, potential_chancellor = self.elect_government()
            government_elected = self.vote_on_government(president, potential_chancellor)

            if not government_elected:
                self.board_state['election_tracker'] += 1
                if self.board_state['election_tracker'] == 3:
                    self.policy_deck = ['Liberal'] * 6 + ['Fascist'] * 11
                    random.shuffle(self.policy_deck)
                    self.board_state['election_tracker'] = 0

            else:
                if self.hitler_elected:
                    if self.verbose:
                        print("Hitler Elected! Fascists Win!")
                    self.game_over = True
                    self.end_state = 2
                    break
                self.policy_phase()
                if self.hitler_executed:
                    if self.verbose:
                        print("Hitler Executed! Liberals Win!")
                    self.end_state = 3
                    break
                self.board_state['election_tracker'] = 0
        return self.end_state


# Example usage:
if __name__ == "__main__":
    num_players = 5
    game = SecretHitlerGame(num_players, verbose=True)
    game.run_game_simulation()
