import pandas as pd
import numpy as np
from pulp import *
from scipy.sparse.csgraph import minimum_spanning_tree,breadth_first_order

class tsp:
    def __init__(self):
        None

    def tsp_exact(self, matrix):
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
      status = problem.solve(CPLEX_CMD) 
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
    
    def nn_heuristic(self, matrix):
        points = list(range(1,len(matrix.loc[0])))
        matrix = matrix.replace(0, np.nan)
        matrix = matrix.iloc[:,1:]
        route=[]
        distance_sum = []
        distance = 0
        position = 0
        while(len(points)>=1):
            arg_min = matrix.loc[position].idxmin()
            distance = distance + matrix.loc[position,arg_min]
            distance_sum.append(distance)
            route.append(arg_min)
            points.remove(arg_min)
            matrix = matrix.drop([arg_min], axis = 1)
            position = arg_min
        route.insert(0,0)
        route.append(0)
        return(route)
    
    def ni_heuristic(self, matrix):
        backup = matrix 
        points = list(range(1,len(matrix[0])))
        matrix = matrix.replace(0, np.nan)
        matrix = matrix.drop(0, axis = 1)
        route=[] 
        route.append(0)
        while(len(points)>=1):
            min = 100000
            for i in route:
                arg_min = matrix.loc[i].idxmin()
                if (route.count(arg_min)) == 0:
                    if (backup.iloc[i, arg_min]<min):
                        min_node = arg_min
                        min = backup.iloc[i, arg_min]
            if len(route)>=3:
                best_position = 10000
                node = 0
                for i in range(len(route)-1):
                    saving = backup.iloc[route[i],min_node] + backup.iloc[min_node, route[i+1]] - backup.iloc[route[i],route[i+1]]
                    if (saving<=best_position):
                        node = i
                        best_position = saving
                route.insert(node+1, min_node)
                points.remove(min_node)
                matrix=matrix.drop([min_node], axis = 1)
            else:
                route.append(min_node)
                points.remove(min_node)
                matrix=matrix.drop([min_node], axis = 1)
        route.append(0)
        return (route)
    
    def ci_heuristic(self,matrix):
        backup = matrix 
        points = list(range(1,len(matrix[0])))
        matrix = matrix.replace(0, np.nan)
        matrix = matrix.drop(0, axis = 1)
        route=[]
        position = 0 
        route.append(0)
        while(len(points)>=1):
            if (len(route))<3:
                for i in route:
                    min_node = matrix.loc[position].idxmin()
                route.append(min_node)
                points.remove(min_node)
                matrix = matrix.drop([min_node], axis = 1)
                position = min_node


            if len(route)>=3:
                min_k=0
                best_position = 10000
                node = 0
                for j in points:
                    min_k = j
                    for i in range(len(route)-1):
                        saving = backup.iloc[route[i],min_node] + backup.iloc[min_node, route[i+1]] - backup.iloc[route[i],route[i+1]]
                        if (saving<=best_position):
                            min_node = min_k
                            node = i
                            best_position = saving
                route.insert(node+1, min_node)
                points.remove(min_node)
                matrix=matrix.drop([min_node], axis = 1)
        route.append(0)
        return (route)
    
    def fi_heuristic(self, matrix):
        backup = matrix 
        points = list(range(1,len(matrix[0])))
        matrix = matrix.replace(0, np.nan)
        matrix = matrix.drop(0, axis = 1)
        route=[]
        route.append(0)
        while(len(points)>=1):
            min = 100000
            for i in route:
                arg_min = matrix.loc[i].idxmax()
                if (route.count(arg_min)) == 0:
                    if (backup.iloc[i, arg_min]<min):
                        min_node = arg_min
                        min = backup.iloc[i, arg_min]
            if len(route)>=3:
                best_position = 10000
                node = 0
                for i in range(len(route)-1):
                    saving = backup.iloc[route[i],min_node] + backup.iloc[min_node, route[i+1]] - backup.iloc[route[i],route[i+1]]
                    if (saving<=best_position):
                        node = i
                        best_position = saving
                route.insert(node+1, min_node)
                points.remove(min_node)
                matrix=matrix.drop([min_node], axis = 1)
            else:
                route.append(min_node)
                points.remove(min_node)
                matrix=matrix.drop([min_node], axis = 1)
        route.append(0)
        return (route)
    
    def MST_heuristic(time_matrix):
        tree = minimum_spanning_tree(time_matrix)
        route = breadth_first_order(tree, i_start=0, directed=False, return_predecessors=False).tolist()
        route.append(0)
        return(route)
