import numpy as np
import os
import multiprocessing
import time

def read_orbital_parameters(body_name):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, f'{body_name}.txt')

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No data file found for {body_name}")

    with open(file_path, 'r') as file:
        params = [float(line.strip()) for line in file.readlines()]

    return tuple(params)

def body_params(body_name, t):
    a, e, i, Omega, omega, M0, T = read_orbital_parameters(body_name)
    return (a, e, np.radians(i), np.radians(Omega), np.radians(omega), M0 + (2 * np.pi / T) * t)

def kepler_equation(E, M, e):
    return E - e * np.sin(E) - M

def solve_kepler(M, e):
    E = M  # Mean Anomaly equal to Eccentric Anomaly (okay if orbits are not too eccentric)
    while True:
        delta = kepler_equation(E, M, e)
        if abs(delta) < 1e-6:  # Tolerance value for sufficient E accuracy
            break
        E -= delta / (1 - e * np.cos(E))
    return E

def true_anomaly(E, e):
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))

def orbital_to_cartesian(a, e, i, Omega, omega, M):
    E = solve_kepler(M, e)
    nu = true_anomaly(E, e)

    # Orbital plane coordinates
    x_prime = a * (np.cos(E) - e)
    y_prime = a * np.sqrt(1 - e**2) * np.sin(E)

    # Rotation matrices
    Rz_Omega = np.array([[np.cos(Omega), -np.sin(Omega), 0],
                         [np.sin(Omega), np.cos(Omega), 0],
                         [0, 0, 1]])

    Rx_i = np.array([[1, 0, 0],
                     [0, np.cos(i), -np.sin(i)],
                     [0, np.sin(i), np.cos(i)]])

    Rz_omega = np.array([[np.cos(omega), -np.sin(omega), 0],
                         [np.sin(omega), np.cos(omega), 0],
                         [0, 0, 1]])

    # Convert to celestial coordinates
    r = np.dot(np.dot(np.dot(Rz_Omega, Rx_i), Rz_omega), np.array([x_prime, y_prime, 0]))

    return r

def calculate_min_max_distance_partial(body1_name, body2_name, M01, T1, M02, T2, time_steps):
    min_distance = np.inf
    max_distance = 0

    for t in time_steps:
        params1 = body_params(body1_name, t)
        params2 = body_params(body2_name, t)
        r1 = orbital_to_cartesian(*params1)
        r2 = orbital_to_cartesian(*params2)
        distance = np.linalg.norm(r1 - r2)

        min_distance = min(min_distance, distance)
        max_distance = max(max_distance, distance)

    return min_distance, max_distance

def format_duration(seconds):
    # Compute hours, minutes, and seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    # Format output string conditionally based on the presence of hours and minutes
    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(seconds)}s"

# Main calculation
if __name__ == "__main__":
    
    # Ask for the names of the two bodies to calculate the distances between: Moho, Eve, Kerbin, Duna, Dres, Jool, Eeloo
    body1_name = input("Enter name of the first body: ")
    body2_name = input("Enter name of the second body: ")

    # Ask for the number of Kerbin years to run the calculation
    kerbin_years = float(input("Enter the number of Kerbin years to run for: "))

    # Read periods and mean anomalies for time step calculation
    _, _, _, _, _, M01, T1 = read_orbital_parameters(body1_name)
    _, _, _, _, _, M02, T2 = read_orbital_parameters(body2_name)

    # Define Kerbin year in seconds
    kerbin_year_seconds = 9203544.61750141

    # Calculate the total duration in seconds for the given number of Kerbin years
    total_duration_seconds = kerbin_years * kerbin_year_seconds

    # Define the time steps over which to calculate based on total_duration_seconds - final parameter can be adjusted to alter step duration in seconds
    total_time_steps = np.arange(0, total_duration_seconds, 3600)

    # Number of processes
    num_processes = multiprocessing.cpu_count()

    # Split time steps into chunks for each process
    chunks = np.array_split(total_time_steps, num_processes)

    # Create a multiprocessing pool
    pool = multiprocessing.Pool(processes=num_processes)

    # Start timing
    start_time = time.time()

    # Map the function to the pool with different chunks of time steps
    results = pool.starmap(calculate_min_max_distance_partial, 
                           [(body1_name, body2_name, M01, T1, M02, T2, chunk) for chunk in chunks])

    # Close the pool and wait for tasks to complete
    pool.close()
    pool.join()

    # End timing
    end_time = time.time()
    calculation_time = end_time - start_time
    formatted_time = format_duration(calculation_time)

    # Combine results from all processes
    min_dist = min(result[0] for result in results)
    max_dist = max(result[1] for result in results)

    # Print results
    print(f"Minimum Distance: {min_dist} meters")
    print(f"Maximum Distance: {max_dist} meters")
    print(f"Calculation Time: {formatted_time}")
