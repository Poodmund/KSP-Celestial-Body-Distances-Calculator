# cython_functions.pyx
import numpy as np
cimport numpy as np

cpdef tuple calculate_body_params(np.ndarray[double, ndim=1] params, double t):
    cdef double a = params[0]
    cdef double e = params[1]
    cdef double i = np.radians(params[2])
    cdef double Omega = np.radians(params[3])
    cdef double omega = np.radians(params[4])
    cdef double M0 = params[5]
    cdef double T = params[6]
    cdef double M = M0 + (2 * np.pi / T) * t
    return (a, e, i, Omega, omega, M)  # Return as tuple

cdef double kepler_equation(double E, double M, double e):
    return E - e * np.sin(E) - M

cpdef double solve_kepler(double M, double e):
    cdef double E = M  # Mean Anomaly equal to Eccentric Anomaly (okay if orbits are not too eccentric)
    cdef double delta
    while True:
        delta = kepler_equation(E, M, e)
        if abs(delta) < 1e-6:  # Tolerance value for sufficient E accuracy
            break
        E -= delta / (1 - e * np.cos(E))
    return E

cpdef double true_anomaly(double E, double e):
    return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))

cpdef np.ndarray[double, ndim=1] orbital_to_cartesian(double a, double e, double i, double Omega, double omega, double M):
    cdef double E = solve_kepler(M, e)
    cdef double nu = true_anomaly(E, e)

    # Orbital plane coordinates
    cdef double x_prime = a * (np.cos(E) - e)
    cdef double y_prime = a * np.sqrt(1 - e**2) * np.sin(E)

    # Rotation matrices
    cdef np.ndarray[double, ndim=2] Rz_Omega = np.array([[np.cos(Omega), -np.sin(Omega), 0],
                                                         [np.sin(Omega), np.cos(Omega), 0],
                                                         [0, 0, 1]])

    cdef np.ndarray[double, ndim=2] Rx_i = np.array([[1, 0, 0],
                                                     [0, np.cos(i), -np.sin(i)],
                                                     [0, np.sin(i), np.cos(i)]])

    cdef np.ndarray[double, ndim=2] Rz_omega = np.array([[np.cos(omega), -np.sin(omega), 0],
                                                         [np.sin(omega), np.cos(omega), 0],
                                                         [0, 0, 1]])

    # Convert to celestial coordinates
    cdef np.ndarray[double, ndim=1] r = np.dot(np.dot(np.dot(Rz_Omega, Rx_i), Rz_omega), np.array([x_prime, y_prime, 0]))
    
    return r

cpdef tuple calculate_min_max_distance_partial(np.ndarray[double, ndim=1] params1, np.ndarray[double, ndim=1] params2, np.ndarray[double, ndim=1] time_steps):
    cdef double min_distance = np.inf
    cdef double max_distance = 0
    cdef double distance
    cdef np.ndarray[double, ndim=1] r1, r2

    for t in time_steps:
        r1 = orbital_to_cartesian(*calculate_body_params(params1, t))
        r2 = orbital_to_cartesian(*calculate_body_params(params2, t))
        distance = np.linalg.norm(r1 - r2)

        if distance < min_distance:
            min_distance = distance
        if distance > max_distance:
            max_distance = distance

    return (min_distance, max_distance)
