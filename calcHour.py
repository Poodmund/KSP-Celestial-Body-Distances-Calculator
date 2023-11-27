import numpy as np
import os
import multiprocessing
import time
import cython_functions

def read_orbital_parameters(body_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'bodies', f'{body_name}.txt')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No data file found for {body_name}")

    with open(file_path, 'r') as file:
        params = [float(line.strip()) for line in file.readlines()]

    if len(params) < 8:
        raise ValueError(f"Not enough data in file for {body_name}. Expected at least 8 values.")

    return np.array(params)  # Convert to a NumPy array

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

def calculate_kerbal_year_seconds():
    kerbal_minute = 60
    kerbal_hour = kerbal_minute * 60
    kerbal_day = kerbal_hour * 6
    kerbal_year = kerbal_day * 426   
    return kerbal_year

# Convert seconds to Kerbal formatted time
def convert_to_kerbal_time_format(seconds):
    kerbal_minute = 60
    kerbal_hour = kerbal_minute * 60
    kerbal_day = kerbal_hour * 6
    kerbal_year = kerbal_day * 426

    years = int(seconds // kerbal_year)
    days = int((seconds % kerbal_year) // kerbal_day)
    hours = int((seconds % kerbal_day) // kerbal_hour)
    minutes = int((seconds % kerbal_hour) // kerbal_minute)
    seconds = int(seconds % kerbal_minute)

    return f"Y{years}:D{days}:{hours}h:{minutes}m:{seconds}s"

# Main calculation
if __name__ == "__main__":
    # Ask for the names of the two bodies to calculate the distances between
    body1_name = input("Enter name of the first body: ")
    body2_name = input("Enter name of the second body: ")

    # Ask for specific times for minimum and maximum distance calculations
    min_distance_time = float(input("Enter the time in seconds for minimum distance calculation: "))
    max_distance_time = float(input("Enter the time in seconds for maximum distance calculation: "))

    # Read orbital parameters of both bodies
    params1 = read_orbital_parameters(body1_name)
    params2 = read_orbital_parameters(body2_name)

    # Define the time steps for each calculation (1 hour before and after the specified times)
    time_steps_min = np.arange(min_distance_time - 3600, min_distance_time + 3600, 1)
    time_steps_max = np.arange(max_distance_time - 3600, max_distance_time + 3600, 1)

    # Number of processes
    num_processes = multiprocessing.cpu_count()

    # Create a multiprocessing pool and calculate distances
    pool = multiprocessing.Pool(processes=num_processes)

    # Start timing
    calculation_start_time = time.time()

    # Calculate minimum distance
    results_min = pool.starmap(cython_functions.calculate_min_max_distance_partial, [(params1, params2, chunk) for chunk in np.array_split(time_steps_min, num_processes)])
    min_dist = min(result[0] for result in results_min)

    # Calculate maximum distance
    results_max = pool.starmap(cython_functions.calculate_min_max_distance_partial, [(params1, params2, chunk) for chunk in np.array_split(time_steps_max, num_processes)])
    max_dist = max(result[2] for result in results_max)

    # Close the pool and wait for tasks to complete
    pool.close()
    pool.join()

    # End timing
    calculation_end_time = time.time()
    calculation_time = calculation_end_time - calculation_start_time
    formatted_time = format_duration(calculation_time)

    # After multiprocessing calculations
    global_min_dist = np.inf
    global_min_time = 0
    global_max_dist = 0
    global_max_time = 0
    
    # Combine results from all processes
    for result in results_min:
        min_dist, min_time, _, _ = result
        if min_dist < global_min_dist:
            global_min_dist, global_min_time = min_dist, min_time
    
    for result in results_max:
        _, _, max_dist, max_time = result
        if max_dist > global_max_dist:
            global_max_dist, global_max_time = max_dist, max_time
    
    # Inside your main calculation block, after you have calculated min_dist, max_dist, min_time, max_time:
    global_min_distance_time_formatted = convert_to_kerbal_time_format(global_min_time)
    global_max_distance_time_formatted = convert_to_kerbal_time_format(global_max_time)
    
    # Print results with actual times of minimum and maximum distances
    print(f"Minimum Distance: {global_min_dist} meters, Time (s): {global_min_time}, Time (Kerbal): {global_min_distance_time_formatted}")
    print(f"Maximum Distance: {global_max_dist} meters, Time (s): {global_max_time}, Time (Kerbal): {global_max_distance_time_formatted}")
