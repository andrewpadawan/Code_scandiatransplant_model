#code adapted from https://www.geeksforgeeks.org/dsa/implement-simulated-annealing-in-python/
import math
import random
from main import run_Scandiatransplant_model
import csv
from datetime import datetime
from metaheuristic.objective_function import objective_aprox_V2
# Objective function: Scandiatransplant output function
"""def objective_function(w_mismatch,w_distance, w_payback):
    print("Calling objective")
    number_matches, total_distance_travelled_incl_local, total_mismatches, average_equity_coefficient= run_Scandiatransplant_model(w_mismatch,w_distance, w_payback)

    max_distance= 5442.19 * number_matches
    distance_prop= ((10* total_distance_travelled_incl_local)/max_distance)
    if distance_prop > 1: 
        distance_prop = 1.0 
    distance_score = 1 - distance_prop

    mismatch_score= 1- (total_mismatches/(6*number_matches))
    
    value= average_equity_coefficient + mismatch_score + distance_score
    print("Value:")
    print(value)
    return value"""

# Neighbor function: small random change

"""Original
def get_neighbor(x, step_size=0.1):
    # Copy the current solution
    neighbor = x[:]
    
    # Pick one index to modify
    index = random.randint(0, len(x) - 1)
    
    # Add a small random perturbation
    neighbor[index] += random.uniform(-step_size, step_size)
    print("Neighbour")
    print(neighbor)
    return neighbor
"""

#new version bounces back from the boundary
"""
def get_neighbor(x, step_size=0.2, bounds=None):
    neighbor = x[:]
    index = random.randint(0, len(x) - 1)

    # Apply perturbation
    neighbor[index] += random.uniform(-step_size, step_size)

    # Reflective boundary handling
    if bounds is not None:
        low, high = bounds[index]

        # If value goes below the lower bound
        if neighbor[index] < low:
            excess = low - neighbor[index]
            neighbor[index] = low + excess   # reflect upward

        # If value goes above the upper bound
        elif neighbor[index] > high:
            excess = neighbor[index] - high
            neighbor[index] = high - excess  # reflect downward

    return neighbor 
    
"""
#Perturb all at once for a wider exploration
def get_neighbor(x, step_size, bounds):
    candidate = []
    for i, (low, high) in enumerate(bounds):
        y = x[i] + random.uniform(-step_size, step_size)

        # reflect
        if y < low:
            y = low + (low - y)
        if y > high:
            y = high - (y - high)

        candidate.append(y)
    return candidate


def get_neighbor_ratio_based(x, step_size, bounds):
    candidate = []
    for i, (low, high) in enumerate(bounds):
        eps = 1e-9
        xi = max(x[i], eps)

        # Work in log space
        log_x = math.log(xi)

        # Perturb multiplicatively
        log_y = log_x + random.uniform(-step_size, step_size)

        # Convert back
        y = math.exp(log_y)

        # --- Reflection instead of clipping ---
        if y < low:
            y = low + (low - y)      # reflect upward
        if y > high:
            y = high - (y - high)    # reflect downward

        candidate.append(y)

    return candidate



def simulated_annealing(objective, bounds, n_iterations, step_size, temp, initial=None):
    # Create timestamped filename 
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") 
    csv_path = f"logs/sa_logs/sa_log_{timestamp}.csv"

    # Create CSV file and write metadata + header
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)

        # --- Metadata block ---
        writer.writerow(["SA_RUN_METADATA"])
        writer.writerow(["initial_state", initial])
        writer.writerow(["step_size", step_size])
        writer.writerow(["temperature", temp])
        writer.writerow(["iterations", n_iterations])
        writer.writerow(["bounds", bounds])
        writer.writerow([])  # blank line for readability

        # --- Column header ---
        writer.writerow(["iteration", "temperature", "current_eval", 
                         "current_solution", "best_eval", "best_solution"])
    
    # --- Initialization ---
    if initial is None:
        current = [random.uniform(b[0], b[1]) for b in bounds]
    else:
        current = initial[:]  # copy to avoid mutation

    best = current[:]
    best_eval = objective(*best)
    current_eval = best_eval
    scores = [best_eval]

    # --- Write the actual initial state to the CSV ---
    with open(csv_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["actual_initial_state", current])


    # --- Main SA loop ---
    for i in range(n_iterations):
        t = temp * (1 - i / n_iterations)
        t = max(t, 1e-9)   # avoid division by zero in acceptance probability

        if t < 1e-3: 
            print(f"Stopping early at iteration {i} because temperature is too cold: {t}") 
            break
        # scale step size with temperature 
        scaled_step = step_size * (t / temp) 
        candidate = get_neighbor_ratio_based(current, scaled_step, bounds)

        #candidate = get_neighbor(current, step_size, bounds)
        candidate_eval = objective(*candidate)

        if (candidate_eval > current_eval or
            random.random() < math.exp((candidate_eval - current_eval) / t)):
            
            current, current_eval = candidate, candidate_eval

            if candidate_eval > best_eval:
                best, best_eval = candidate[:], candidate_eval
                scores.append(best_eval)

        # Append row to CSV
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([i, t, current_eval, current, best_eval, best])

        if i % 100 == 0:
            print(f"Iteration {i}, Temp {t:.3f}, Candidate Eval {candidate_eval:.5f}, "
                  f"Current Eval {current_eval:.5f}, Best Eval {best_eval:.10f}")

    return best, best_eval, scores



# Define problem domain
bounds = [(0.0, 1000.0) for _ in range(2)] # for a 2-dimensional function
#n_iterations = 1000
n_iterations= 300
step_size = 0.3 #0.5 are big jumps
temp = 2
#initial = [750.0, 200.0, 100.0]
#initial= [1000, 1, 1000]
# Perform the simulated annealing search
#best, score, scores = simulated_annealing(objective_aprox, bounds, n_iterations, step_size, temp)

#print(f'Best Solution: {best}')
#print(f'Best Score: {score}')

n_runs = 20  # however many you want
all_results = []

global_best = None
global_best_score = -float("inf")

for run in range(n_runs):
    print(f"\n=== SA RUN {run+1}/{n_runs} ===")

    best, score, scores = simulated_annealing(
        objective_aprox_V2,
        bounds,
        n_iterations,
        step_size,
        temp,
        initial=None   # ensures random start
    )

    all_results.append((best, score))

    if score > global_best_score:
        global_best_score = score
        global_best = best

print("\n=== SUMMARY OF ALL RUNS ===")
print("Global best solution:", global_best)
print("Global best score:", global_best_score)


#objective_function(100, 198.00354526869708, 425.6148983082172)