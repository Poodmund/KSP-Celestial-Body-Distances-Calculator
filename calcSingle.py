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

# Main calculation
if __name__ == "__main__":

    # Ask for the names of the two bodies to calculate the distances between: Moho, Eve, Kerbin, Duna, Dres, Jool, Eeloo, Sarnus, Urlum, Neidon, Plock
    body1_name = input("Enter name of the first body: ")
    body2_name = input("Enter name of the second body: ")

    # Ask for the start and end years for the calculation
    start_year = float(input("Enter the start Kerbal year: "))
    end_year = float(input("Enter the end Kerbal year: "))
    
    # Read orbital parameters of both bodies
    params1 = read_orbital_parameters(body1_name)
    params2 = read_orbital_parameters(body2_name)

    # Define Kerbin year in seconds
    kerbin_year_seconds = 9203544.61750141

    # Define Kerbal year in seconds (426 * 6hr days)
    kerbal_year_seconds = calculate_kerbal_year_seconds()

    # Calculate the start and end times in seconds
    start_time_seconds = start_year * kerbal_year_seconds
    end_time_seconds = end_year * kerbal_year_seconds

    # Define the time steps over which to calculate based on total_duration_seconds - final parameter can be adjusted to alter step duration in seconds
    total_time_steps = np.arange(start_time_seconds, end_time_seconds, 3600)

    # Number of processes
    num_processes = multiprocessing.cpu_count()

    # Split time steps into chunks for each process
    chunks = np.array_split(total_time_steps, num_processes)

    # Create a multiprocessing pool
    pool = multiprocessing.Pool(processes=num_processes)

    # Start timing
    calculation_start_time = time.time()

    # Use pool.starmap to process chunks
    results = pool.starmap(cython_functions.calculate_min_max_distance_partial, 
                           [(params1, params2, chunk) for chunk in chunks])

    # Close the pool and wait for tasks to complete
    pool.close()
    pool.join()
    
    # End timing
    calculation_end_time = time.time()
    calculation_time = calculation_end_time - calculation_start_time
    formatted_time = format_duration(calculation_time)

    # Processing results to find global minimum and maximum distances
    global_min_dist = np.inf
    global_min_time = 0
    global_max_dist = 0
    global_max_time = 0

    # Combine results from all processes
    for result in results:
        min_dist, min_time, max_dist, max_time = result
        if min_dist < global_min_dist:
            global_min_dist, global_min_time = min_dist, min_time
        if max_dist > global_max_dist:
            global_max_dist, global_max_time = max_dist, max_time

    # Print results
    print(f"Minimum Distance: {global_min_dist} meters at time {global_min_time}s")
    print(f"Maximum Distance: {global_max_dist} meters at time {global_max_time}s")
    print(f"Calculation Time: {formatted_time}")