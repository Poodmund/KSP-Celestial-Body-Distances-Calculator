import numpy as np
import os
import multiprocessing
import time
import cython_functions

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


def get_all_body_names(exclude_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    bodies_dir = os.path.join(script_dir, 'bodies')
    body_files = [f.replace('.txt', '') for f in os.listdir(bodies_dir) if os.path.isfile(os.path.join(bodies_dir, f))]
    return [name for name in body_files if name != exclude_name]

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

# Main calculation
if __name__ == "__main__":
    
    # Ask for the name of the initial body: Moho, Eve, Kerbin, Duna, Dres, Jool, Eeloo, Sarnus, Urlum, Neidon, Plock
    body1_name = input("Enter name of the first body: ")
    
    # Ask for the number of Kerbin years to run the calculation
    kerbin_years = float(input("Enter the number of Kerbin years to run for: "))

    # Read orbital parameters of body1
    params1, a1 = read_orbital_parameters_with_a(body1_name)
    
    # Define Kerbin year in seconds
    kerbin_year_seconds = 9203544.61750141
    
    # Calculate the total duration in seconds for the given number of Kerbin years
    total_duration_seconds = kerbin_years * kerbin_year_seconds
    
    # Define the time steps over which to calculate based on total_duration_seconds - final parameter can be adjusted to alter step duration in seconds
    total_time_steps = np.arange(0, total_duration_seconds, 3600)
    
    # Number of processes
    num_processes = multiprocessing.cpu_count()

    # Get orbital parameters of all other bodies
    other_bodies = get_all_body_names(body1_name)
    bodies_with_a = []

    for body2_name in other_bodies:
        _, a2 = read_orbital_parameters_with_a(body2_name)
        bodies_with_a.append((body2_name, a2))

    # Sort bodies by their semi-major axis
    sorted_bodies = sorted(bodies_with_a, key=lambda x: x[1])

    # Start timing
    start_time = time.time()

    # Map the function to the pool with different chunks of time steps for each body sequentially
    for body2_name, _ in sorted_bodies:
        params2, _ = read_orbital_parameters_with_a(body2_name)
        chunks = np.array_split(total_time_steps, num_processes)
        pool = multiprocessing.Pool(processes=num_processes)

        results = pool.starmap(cython_functions.calculate_min_max_distance_partial, 
                               [(params1, params2, chunk) for chunk in chunks])
        
        # Close the pool and wait for tasks to complete
        pool.close()
        pool.join()

        # Combine results from all processes
        min_dist = min(result[0] for result in results)
        max_dist = max(result[1] for result in results)
        
        # Print results
        print(f"Minimum Distance between {body1_name} and {body2_name}: {min_dist} meters")
        print(f"Maximum Distance between {body1_name} and {body2_name}: {max_dist} meters")

    # End timing
    end_time = time.time()
    calculation_time = end_time - start_time
    formatted_time = format_duration(calculation_time)
    
    # Print total duration
    print(f"Total Calculation Time: {formatted_time}")
