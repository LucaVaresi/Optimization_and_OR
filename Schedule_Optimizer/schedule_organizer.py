import pandas as pd
import signal
from mip import Model, xsum, maximize, BINARY
from itertools import product
import time
import numpy as np
from tabulate import tabulate

# day start at 8 and ends at 14
data ={"Time":[60,40,80,50,60,30, 60, 120, 30, 60, 120],
"Activity name":["watch anime","exercise","go to swim", "go running","have lunch","have breakfast",
                 "play video game short","play video game long","read a good book",
                 "do a coding tutorial short", "do a coding tutorial long"],

"Satisfaction":[7,7,8,8,3,3,7,8,6,9,10],
"Energy needed":[0,3,4,5,0,0,0,0,3,6,8]
}
df = pd.DataFrame.from_dict(data)

# Specify min and max start time (hour)
df.loc[df["Activity name"].str.contains("breakfast"),"End Before"] = 11
df.loc[df["Activity name"].str.contains("lunch"),"Start After"] = 12
df.loc[df["Activity name"].str.contains("exercise|swim|run|coding"),"Start After"] = 9

# Specify if an activity must be done in the time window
df["Must_Do"] = False
df.loc[df["Activity name"].str.contains("breakfast|lunch"),"Must_Do"] = True

# df.to_csv("morning_activies.csv")
# df = pd.read_csv("morning_activies.csv")

# starting
start = time.time()

#####################################################################################################
# Metadata
day_start = 8 # day starts at 8 Am

##########################
#  SETS
##########################

# Set of activities
I = set(range(df.shape[0]))

# Set of time instant in minutes, time start at 8AM and ends at 14
T = set(range(360))

# sets of activities i that has a start date, a end date, must be done
S = set(df[df["Start After"].notnull()].index)
E = set(df[df["End Before"].notnull()].index)

##########################
#  Parameters
##########################

# Satisfaction of each activity
w = df["Satisfaction"].tolist()

# Energy cost
e = df["Energy needed"].tolist()

# Time needed to complete the activity
d = df["Time"]

# Max energy, since I am not a morning howl i specificy a max energy available ;)
Me = 12

# activies must be done 
O = df["Must_Do"]*1

##########################
#  Model definition
##########################

m = Model("morning_schedule")

# binary variables indicating if activity i starts at time t
x = [[m.add_var(name='activity_start_in_t',var_type=BINARY) for t in T] for i in I]

# binary variables indicating if activity i is done
y = [m.add_var(name='activity_done') for i in I]


m.objective = maximize(xsum(y[i]*w[i] for i in I))

# minimum number of people in office satisfied

for i in I: # compulsory activity should be done, y>=0
    m += y[i] >= O[i]

for i in I: # y <= 1
    m += y[i] <= 1
# max energy
m += xsum(y[i]*e[i] for i in I) <= Me

for i in S : # min start
    m += xsum(t*x[i][t] for t in T) >= (df.loc[i,"Start After"]-day_start)*60*y[i]

for i in E : # max end
    m += xsum(t*x[i][t] for t in T) <= ((df.loc[i,"End Before"]-day_start)*60 - d[i]) + len(T)*(1-y[i])

for i in I: # Link y and x variables, y=1 => exist and x=1
    m += y[i] == xsum(x[i][t]  for t in T)

for i in I:  # do one activity at most once
    m += xsum(x[i][t]  for t in T) <= 1

    
for (i, t) in product(I,T): # do at most one activity at once part 1
    m += x[i][t] <= 1 - xsum(x[j][tau] if (j!=i & tau>=t-d[j]+1) else 0
                             for j in I for tau in set(range(t+d[i]))) #{t-d[j]+1, ... t+d[i]-1}


m.optimize()

#####################################################################################################

# Rewrite result format

intermediate = time.time()
print(f"intermediate time elapsed: {intermediate - start}")

df["Starting_Time_min"]=np.nan
#df["Ending_Time"]=np.nan

change_i = ""
for i,t in product(I,T):
    if(i!=change_i):
        if(y[i].x==0):
            change_i = i
            continue  
        if(x[i][t].x>0):
           df.loc[i,"Starting_Time_min"] = 60*8 + t
           #df.loc[i,"Ending_Time"] = 60*8 + t + d[i]
           change_i = i
           print(f"i: {i}, t: {t}")

end = time.time()
print(f"time elapsed: {end - start}\n")
print(f"optimal solution provide satisfaction: {m.objective_value}\n")

df["Starting_Time"] = df["Starting_Time_min"]
df["Ending_Time"] = df["Starting_Time_min"] + df["Time"]


df.loc[~df["Starting_Time"].isnull(),"Starting_Time"] = (
    (df.loc[~df["Starting_Time"].isnull(),"Starting_Time"]//60).astype(int).astype(str)
    + "h " 
    + (df.loc[~df["Starting_Time"].isnull(),"Starting_Time"]%60).astype(int).astype(str) + "m")

df.loc[~df["Ending_Time"].isnull(),"Ending_Time"] = (
    (df.loc[~df["Ending_Time"].isnull(),"Ending_Time"]//60).astype(int).astype(str)
    + "h " 
    + (df.loc[~df["Ending_Time"].isnull(),"Ending_Time"]%60).astype(int).astype(str) + "m")

output_df = df.sort_values(
                by="Starting_Time_min")[
                ["Activity name","Starting_Time",
                "Ending_Time", "Energy needed","Satisfaction"]
]
print("Variable selected solving the schedule:\n")

for i in range(11):
    if(y[i].x==1):
        print(f"y[{i}] = {y[i].x}")

skip_i = ""
for i,t in product(I,T):
    if(skip_i!=i):
        if(y[i].x!=1):
            skip_i = i
            continue  
        if(x[i][t].x>0):
           change_i = i
           print(f"x[{i},{t+8*60}] = {x[i][t].x} ")

print(tabulate(output_df, headers='keys', tablefmt='psql'))
