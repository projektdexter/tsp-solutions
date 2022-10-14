
import pandas as pd
import numpy as np
from pulp import LpMinimize

class tsp:
  def __init__(self):
    pass 

  def TSP_truck(self, matrix):
      result = []
      result_name = []
      result_df = pd.DataFrame()
      row,col = matrix.shape
      
      problem = LpProblem('TravellingSalesmanProblem', LpMinimize)

      # Decision variable X for truck route
      decisionVariableX = LpVariable.dicts('decisionVariable_X', ((i, j) for i in range(row) for j in range(row)), lowBound=0, upBound=1, cat='Integer')

      # subtours elimination
      decisionVariableU = LpVariable.dicts('decisionVariable_U', (i for i in range(row)), lowBound=1, cat='Integer')

      # Decision variable T for truck arrival time
      decisionVariableT = LpVariable.dicts('decisionVariable_T', (i for i in range(row)), lowBound=0, cat='Float')

      # Objective Function
      problem += lpSum(decisionVariableT[i] for i in range(row))

      # Constraint
      for i in range(row):
          problem += (decisionVariableX[i,i] == 0) # elimination of (1 to 1) route
          if i==0:
              problem += (decisionVariableT[i] == 0) # elimination of (1 to 1) route
          problem += lpSum(decisionVariableX[i,j] for j in range(row))==1 # truck reaches all points once
          problem += lpSum(decisionVariableX[j,i] for j in range(row)) ==1 #truck dispatches from all points once
          for j in range(row):
              if i != j and (i != 0 and j != 0):
                  problem += decisionVariableU[i]  <=  decisionVariableU[j] + row * (1 - decisionVariableX[i, j])-1 # sub-tour elimination for truck
              if i != j and (j != 0):
                  problem += decisionVariableT[j] >= decisionVariableT[i] + matrix.iloc[i,j] - 10000*(1-decisionVariableX[i,j]) # Calculating time of arrival at each node
      
      # Solving the equation and storing the result
      status = problem.solve() 
      for var in problem.variables():
          if (problem.status == 1):
              if (var.value() !=0):
                  result.append(var.value())
                  result_name.append(var.name)
      result_df['Variable Name'] = result_name
      result_df['Variable Value'] = result
   
      # creating route list      
      route = [0]*row
      for x,value in enumerate(route):
        for j in range(row):
          if (pulp.value(decisionVariableX[value,j])==1):
            if (j!=0):
              route[x+1] = j
      route.append(0)


      # return
      return(problem.objective.value(), problem.solutionTime, result_df, route)
