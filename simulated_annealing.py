#code adapted from https://www.geeksforgeeks.org/dsa/implement-simulated-annealing-in-python/
import math
import random
from main import run_Scandiatransplant_model
import csv
from datetime import datetime
# Objective function: Rastrigin function
def objective_function(w_mismatch,w_distance, w_payback):
    number_matches, total_distance_travelled_incl_local, total_mismatches, average_equity_coefficient= run_Scandiatransplant_model(w_mismatch,w_distance, w_payback)

    max_distance= 5442.19 * number_matches
    distance_score= 1- (total_distance_travelled_incl_local/max_distance)
    mismatch_score= 1- (total_mismatches/(6*number_matches))
    
    value= average_equity_coefficient + mismatch_score + distance_score
    return value

# Neighbor function: small random change
def get_neighbor(x, step_size=0.1):
    neighbor = x[:]
    index = random.randint(0, len(x) - 1)
    neighbor[index] += random.uniform(-step_size, step_size)
    return neighbor

def get_neighbor(x, step_size=0.1):
    # Copy the current solution
    neighbor = x[:]
    
    # Pick one index to modify
    index = random.randint(0, len(x) - 1)
    
    # Add a small random perturbation
    neighbor[index] += random.uniform(-step_size, step_size)
    
    return neighbor



def simulated_annealing(objective, bounds, n_iterations, step_size, temp):
    # Create timestamped filename 
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
    csv_path = f"logs/sa_logs/sa_log_{timestamp}.csv"
    # Create CSV file and write header 
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f) 
        writer.writerow(["iteration", "temperature", "best_eval"])
    # Initial solution (random within bounds)
    best = [random.uniform(b[0], b[1]) for b in bounds]
    best_eval = objective(*best)   # unpack weights
    current, current_eval = best[:], best_eval
    scores = [best_eval]

    for i in range(n_iterations):
        # Temperature schedule
        t = temp / float(i + 1)

        # Generate neighbor
        candidate = get_neighbor(current, step_size)

        # Evaluate neighbor
        candidate_eval = objective(*candidate)

        # Accept if better OR probabilistically if worse
        if (candidate_eval > current_eval or
            random.random() < math.exp((candidate_eval - current_eval) / t)):
            
            current, current_eval = candidate, candidate_eval

            # Track global best
            if candidate_eval > best_eval:
                best, best_eval = candidate[:], candidate_eval
                scores.append(best_eval)

        # Log to CSV 
        with open(csv_path, "a", newline="") as f: 
            writer = csv.writer(f) 
            writer.writerow([i, t, best_eval])
        # Optional progress print
        if i % 100 == 0:
            print(f"Iteration {i}, Temp {t:.3f}, Best {best_eval:.5f}")

    return best, best_eval, scores

# Define problem domain
bounds = [(-5.0, 5.0) for _ in range(3)] # for a 3-dimensional function
n_iterations = 3
step_size = 0.2
temp = 10

# Perform the simulated annealing search
best, score, scores = simulated_annealing(objective_function, bounds, n_iterations, step_size, temp)

print(f'Best Solution: {best}')
print(f'Best Score: {score}')