# Optimization_and_OR

### Description
This Repo will be a collection of different tests and implementation of various problems solved with Operational Research and Optimization.

### Structure

#### Schedule_Optimizer
The folder contains an implementation of the following scheduling problem:
Have you ever felt overwhelmed by too many different things to do, without knowing in which order to approach them?
The scheduler optimizer will solve your problem!
The scripts operate with a dataframe with the following columns: 
  ['Time', 'Activity name', 'Satisfaction', 'Energy needed', 'Start After', 'End Before', 'Must_Do']
  
Given this input, if a feasible solution exists, the output provides the starting and ending times of all activities in the solution.
The following constraints are applied: activities marked as Must_Do should be selected, and activities starting and ending time should be coherent with values within "Start After" and "End Before columns".
Moreover, the total energy required by the activities (specified by the "Energy needed" column) should not be more than the maximum energy.
The goal is to select the activities that provide the maximum satisfaction to the user without violating these constraints.

The problem is implemented with both a python script and a Jupyter notebook (they are equivalent w.r.t. the code content)
The time interval in the problem is set from 8 AM to 2 PM, the maximum energy is set to 12

the scripts were runned with Python 3.10.6, the library used are specified in the OR_requirements.txt
