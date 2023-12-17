from game import SecretHitlerGame

class Simulation:
    def __init__(self, num_players, num_simulations):
        self.num_players = num_players
        self.num_simulations = num_simulations
        self.results = {0: 0, 1: 0, 2: 0, 3: 0}  # Distribution of wins (0: Liberals, 1: Fascists, 2: Hitler)

    def run_simulations(self):
        for _ in range(self.num_simulations):
            game = SecretHitlerGame(self.num_players)
            end_state = game.run_game_simulation()
            self.results[end_state] += 1

    def get_results(self):
        total = sum(self.results.values())
        distribution = {end_state: count / total for end_state, count in self.results.items()}
        return distribution

# Example usage:
if __name__ == "__main__":
    num_players = 10
    num_simulations = 1000

    simulation = Simulation(num_players, num_simulations)
    simulation.run_simulations()
    results = simulation.get_results()
    print(f"Distribution of wins after {num_simulations} simulations:")
    print(f"Liberals Win: {results[0]:.2f}")
    print(f"Fascists Win: {results[1]:.2f}")
    print(f"Hitler Elected: {results[2]:.2f}")
    print(f"Hitler Executed: {results[3]:.2f}")
