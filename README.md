# KSP-Celestial-Body-Distances-Calculator
A set of python scripts that can be run to determine the maximum and minimum distances between celestial bodies from Kerbal Space Program over specified time periods.

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
This will run the Cython compilation process. Following this, you can run, either, the script to calculate the distance between two bodies (calcSingle.py), the script to calculate the distances between all bodies (calcAll.py) or the script to calculate the distance between two bodies at a specified time at a 1 second resolution over two hours (calcHour.py), by running the commands:
```
calcSingle.py
```
```
calcAll.py
```
```
calcHour.py
```

3. Enter your calculation details

The following information is required to be entered by the user for calcSingle.py:
- First celestial body
- Second celestial body
- Start year to determination calculation range (in Kerbin years)
- End year to determination calculation range (in Kerbin years)

The following information is required to be entered by the user for calcAll.py:
- Period of time to iterate over from year 0 (in Kerbin years)

The following information is required to be entered by the user for calcHour.py:
- First celestial body
- Second celestial body
- Time (epoch in seconds) for the minimum distance calculation
- Time (epoch in seconds) for the maximum distance calculation

4. The calculation will run and will return the results and the total duration taken to calculate.

## Celestial bodies list
- Moho
- Eve
- Kerbin
- Duna
- Dres
- Jool
- Eeloo
- Sarnus
- Urlum
- Neidon
- Plock

Additional celestial bodies can be added by following the same format as the included file 'Template.txt'.

## Changing the iteration time step value

The scripts are currently set up to iterate over celestial bodies positions each hour (3600 seconds) except for calcHour.py which has a 1 second resolution. This value can be adjusted in calcSingle.py and calcAll.py to affect the accuracy of the calculation. Please note that this also affects total calculation duration.
```
    # Define the time steps over which to calculate based on total_duration_seconds - final parameter can be adjusted to alter step duration in seconds
    total_time_steps = np.arange(0, total_duration_seconds, 3600)
```

## Example

Here is an example of the calculation being run with the output on an Intel i9-9900KS @ 4.8GHz all core workload.
```
>calcSingle.py
Enter name of the first body: Kerbin
Enter name of the second body: Duna
Enter the number of Kerbin years to run for: 1000
Minimum Distance: 6069286587.329437 meters
Maximum Distance: 35383027778.77004 meters
Calculation Time: 18s
```