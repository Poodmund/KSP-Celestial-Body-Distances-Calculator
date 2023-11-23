# KSP-Celestial-Body-Distances-Calculator
A python script that can be run to determine the maximum and minimum distances between two celestial bodies from Kerbal Space Program over a specified time period from Day 0 in Kerbin years.

## Installation

1. Install Python, NumPy, Cython and SetupTools

Download and install Python (https://www.python.org/downloads/). Following Python installation, open your command prompt and enter the following commands:
```
pip install numpy
pip install cython
pip install setuptools
```

2. Run the script

Download this repository and, in your command prompt, navigate to the repository folder. Run the following command:
```
setup.py build_ext --inplace
```
This will run the Cython compilation process. Following this, you can run the calculation by running the command:
```
calc.py
```

3. Enter your calculation details

The following information is required to be entered by the user:
- First celestial body
- Second celestial body
- Period of time to iterate over (in Kerbin years)

4. The calculation will run and will return the results and the total duration taken to calculate.

## Celestial bodies list
- Moho
- Eve
- Kerbin
- Duna
- Dres
- Jool
- Eeloo

Additional celestial bodies can be added by following the same format as the included file 'Template.txt'.

## Changing the iteration time step value

The script is currently set up to iterate over celestial bodies positions each hour (3600 seconds). This value can be adjusted to affect the accuracy of the calculation. Please note that this also affects total calculation duration.
```
    # Define the time steps over which to calculate based on total_duration_seconds - final parameter can be adjusted to alter step duration in seconds
    total_time_steps = np.arange(0, total_duration_seconds, 3600)
```

## Example

Here is an example of the calculation being run with the output on an Intel i9-9900KS @ 4.8GHz all core workload.
```
>calc.py
Enter name of the first body: Kerbin
Enter name of the second body: Duna
Enter the number of Kerbin years to run for: 1000
Minimum Distance: 6069286587.329437 meters
Maximum Distance: 35383027778.77004 meters
Calculation Time: 18s
```