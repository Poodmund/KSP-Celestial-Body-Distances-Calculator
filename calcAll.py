import numpy as np
import os
import multiprocessing
import time
import cython_functions
import itertools

def read_orbital_parameters_with_a(body_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'bodies', f'{body_name}.txt')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No data file found for {body_name}")

    with open(file_path, 'r') as file:
        params = [float(line.strip()) for line in file.readlines()]

    if len(params) < 8:
        raise ValueError(f"Not enough data in file for {body_name}. Expected at least 8 values.")

    semi_major_axis = params[0]
    return np.array(params), semi_major_axis  # Convert to a NumPy array

def get_all_body_names_and_a():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    bodies_dir = os.path.join(script_dir, 'bodies')
    body_files = [f.replace('.txt', '') for f in os.listdir(bodies_dir) if os.path.isfile(os.path.join(bodies_dir, f))]

    bodies_with_a = []
    for body_name in body_files:
        _, semi_major_axis = read_orbital_parameters_with_a(body_name)
        bodies_with_a.append((body_name, semi_major_axis))

    sorted_bodies = sorted(bodies_with_a, key=lambda x: x[1])
    return [body[0] for body in sorted_bodies]

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

def convert_to_kerbal_time(seconds):
    kerbal_minute = 60
    kerbal_hour = kerbal_minute * 60
    kerbal_day = kerbal_hour * 6
    kerbal_year = kerbal_day * 426

    years = seconds // kerbal_year
    days = (seconds % kerbal_year) // kerbal_day
    hours = (seconds % kerbal_day) // kerbal_hour
    minutes = (seconds % kerbal_hour) // kerbal_minute
    seconds = seconds % kerbal_minute

    return f"Y{int(years)}:D{int(days)}:{int(hours)}h:{int(minutes)}m:{int(seconds)}s"

def calculate_distances_for_all_combinations(kerbin_years, num_processes, total_time_steps):
    all_bodies_sorted = get_all_body_names_and_a()

    for body1_name, body2_name in itertools.combinations(all_bodies_sorted, 2):
        params1, _ = read_orbital_parameters_with_a(body1_name)
        params2, _ = read_orbital_parameters_with_a(body2_name)

        chunks = np.array_split(total_time_steps, num_processes)
        pool = multiprocessing.Pool(processes=num_processes)

        results = pool.starmap(cython_functions.calculate_min_max_distance_partial, 
                               [(params1, params2, chunk) for chunk in chunks])
        
        pool.close()
        pool.join()

        # Processing results to find global minimum and maximum distances and their corresponding times
        global_min_dist = np.inf
        global_min_time = 0
        global_max_dist = 0
        global_max_time = 0

        for result in results:
            min_dist, min_time, max_dist, max_time = result
            if min_dist < global_min_dist:
                global_min_dist, global_min_time = min_dist, min_time
            if max_dist > global_max_dist:
                global_max_dist, global_max_time = max_dist, max_time

        kerbal_formatted_min_time = convert_to_kerbal_time(global_min_time)
        kerbal_formatted_max_time = convert_to_kerbal_time(global_max_time)
        
        print(f"Minimum Distance between {body1_name} and {body2_name}: {global_min_dist} meters, Time (s): {global_min_time}, Time (Kerbal): {kerbal_formatted_min_time}")
        print(f"Maximum Distance between {body1_name} and {body2_name}: {global_max_dist} meters, Time (s): {global_max_time}, Time (Kerbal): {kerbal_formatted_max_time}")

if __name__ == "__main__":
    
    # Define Kerbin year in seconds
    kerbin_year_seconds = 9203544.61750141
    
    # Ask for the number of Kerbin years to run the calculation
    kerbin_years = float(input("Enter the number of Kerbin years to run for: "))
    
    # Calculate the total duration in seconds for the given number of Kerbin years
    total_duration_seconds = kerbin_years * kerbin_year_seconds
    
    # Define the time steps over which to calculate based on total_duration_seconds - final parameter can be adjusted to alter step duration in seconds
    total_time_steps = np.arange(0, total_duration_seconds, 3600)

    # Number of processes
    num_processes = multiprocessing.cpu_count()

    # Start timing
    start_time = time.time()
    
    # Run calculation for distances between all combinations of bodies and print results
    calculate_distances_for_all_combinations(kerbin_years, num_processes, total_time_steps)
    
    # End timing
    end_time = time.time()

    # Print total duration
    calculation_time = end_time - start_time
    formatted_time = format_duration(calculation_time)
    print(f"Total Calculation Time: {formatted_time}")
