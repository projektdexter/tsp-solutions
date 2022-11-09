import pandas as pd
import numpy as np
from pulp import *
from scipy.sparse.csgraph import minimum_spanning_tree,breadth_first_order
import copy

class tsp:
    '''
    class instance initiaton
    '''
    def __init__(self):
        None

    '''
    Exact formulation of TSP
    '''
    def tsp_exact(self, matrix, method = "", message = 0):

    #   if isinstance(matrix.columns[0], str):
    #     print("Error: Column index should be INT") 
    #     return None

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

      # objective variable
      z = LpVariable("Objective_z", lowBound=0, cat='Float')

      # Objective Function
      problem += z + lpSum(matrix.iloc[i,0] * decisionVariableX[i, 0] for i in range(row))

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
      
      # last stop time
      for i in range(row):
          problem += decisionVariableT[i] <= z

      # Solving the equation and storing the result
      if method == "CPLEX_CMD":
        status = problem.solve(CPLEX_CMD(msg=message)) 
      if method == "GUROBI_CMD":
        status = problem.solve(GUROBI_CMD(msg=message)) 
      if method == "COIN_CMD":
        status = problem.solve(COIN_CMD(msg=message)) 
      if method == "":
        status = problem.solve(PULP_CBC_CMD(msg=message)) 
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
    
      # return final route and objective value(trip completion time)
      return(route, problem.objective.value())
    

    '''
    Nearest neighbour heuristic
    '''
    def nn_heuristic(self, matrix):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        
        points = list(range(1,len(matrix.loc[0])))
        backup = matrix
        matrix = matrix.replace(0, np.nan)
        matrix = matrix.iloc[:,1:]
        route=[]
        route_sum=0
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
        for i in range(len(route)-1):
            route_sum= route_sum+backup.iloc[route[i], route[i+1]]
        return(route, route_sum) # returns final route and route sum


    '''
    Nearest insertion heuristic
    '''
    def ni_heuristic(self, matrix):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        backup = matrix 
        points = list(range(1,len(matrix.loc[0])))
        matrix = matrix.replace(0, np.nan)
        matrix = matrix.drop(0, axis = 1)
        route=[] 
        route_sum=0
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

        for i in range(len(route)-1):
            route_sum= route_sum+backup.iloc[route[i], route[i+1]]
        return (route, route_sum) # returns final route
    

    '''
    Cheapest insertion heuristic
    '''
    def ci_heuristic(self,matrix):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        backup = matrix 
        route_sum=0
        points = list(range(1,len(matrix.loc[0])))
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

        for i in range(len(route)-1):
            route_sum= route_sum+backup.iloc[route[i], route[i+1]]
        return (route, route_sum) # returns final route


    '''
    Farthest insertion heuristic
    '''
    def fi_heuristic(self, matrix):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        backup = matrix 
        route_sum=0
        points = list(range(1,len(matrix.loc[0])))
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

        for i in range(len(route)-1):
            route_sum= route_sum+backup.iloc[route[i], route[i+1]]
        return (route, route_sum)
    

    '''
    MST  heuristic
    '''
    def MST_heuristic(self, matrix):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        route_sum=0
        tree = minimum_spanning_tree(matrix)
        route = breadth_first_order(tree, i_start=0, directed=False, return_predecessors=False).tolist()
        route.append(0)

        for i in range(len(route)-1):
            route_sum= route_sum+matrix.iloc[route[i], route[i+1]]
        return(route, route_sum)

    
    '''
    2-Opt Improvement  heuristic
    '''
    def Opt2(self, route, matrix, trials=5000):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        route_sum=0
        for i in range(len(route)-1):
            route_sum= route_sum+matrix.iloc[route[i], route[i+1]]

        for i in range(trials):
            previous_obj = route_sum
            backup=route
            a=np.random.randint(1,len(route)-2)
            b=np.random.randint(1,len(route)-2)
            if (a-b >1) or (b-a >1):
                v1=route[a]
                v2=route[a+1]
                v3=route[b]
                v4=route[b+1]
                route[a]=v3
                route[a+1]=v4
                route[b]=v1
                route[b+1]=v2
            new_route_sum=0
            for j in range(len(route)-1):
                new_route_sum= new_route_sum+matrix.iloc[route[j], route[j+1]]
            if (new_route_sum<previous_obj):
                route_sum=new_route_sum
            else:
                route=backup

        return (route, route_sum)
    
    
    '''
    Tabu search
    '''
    def tabu_search(self, route, matrix, trials=5000):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
    
        route_backup= copy.deepcopy(route)
        tabu_step=[]
        route_sum=0
        for i in range(len(route)-1):
            route_sum= route_sum+matrix.iloc[route[i], route[i+1]]
        tabu_list=[]
        tabu_list.append(route_backup)
        for i in range(trials):
            previous_obj = copy.deepcopy(route_sum)
            backup=copy.deepcopy(route)
            a=np.random.randint(1,len(route)-1)
            b=np.random.randint(1,len(route)-1)
            v1=route[a]
            v2=route[b]
            route[a]=v2
            route[b]=v1
            count=0
            for k in tabu_list:
                if (route == k):
                    count=count+1
            if count==0:
                new_route_sum=0
                for j in range(len(route)-1):
                    new_route_sum= new_route_sum+matrix.iloc[route[j], route[j+1]]
                if (new_route_sum<previous_obj):
                    route_sum=copy.deepcopy(new_route_sum)
                    tabu_list.append(copy.deepcopy(route))
                    tabu_step.append(i)
                if (new_route_sum>previous_obj):
                    s = np.random.normal(0.5, 0.1)
                    if s>0.9:
                        route_sum=copy.deepcopy(new_route_sum)
                        tabu_list.append(copy.deepcopy(route))
                        tabu_step.append(i)        
                else:
                    route=copy.deepcopy(backup)

        tabu_route_sum=0
        lowest_sum = float('inf')
        lowest_route = []
        for items in tabu_list:
            tabu_route_sum=0
            for j in range(len(items)-1):
                tabu_route_sum= tabu_route_sum+ matrix.iloc[items[j], items[j+1]]
            if tabu_route_sum<lowest_sum:
                lowest_sum = tabu_route_sum
                lowest_route = items
        
        return (lowest_route, lowest_sum)

    
    '''
    Grid Search for heuristics 
    '''
    def grid_search(self, matrix, heuristics_list):

        if isinstance(matrix.columns[0], str):
            print("Error: Column index should be INT") 
            return None
        result = pd.DataFrame(columns=list(range(0,len(matrix.index)+3)))
        for i in heuristics_list:
            func = getattr(tsp, i)
            route,route_sum = func(self, matrix)
            route.append(route_sum)
            route.insert(0,i)
            result.loc[len(result.index)] = route
        return result



a = pd.read_csv('Hamilton_road_distance.csv')
a.columns = a.columns.astype(int)
print(a)

sol = tsp()

res = sol.tsp_exact(a, method='CPLEX_CMD')
# res = sol.ni_heuristic(a)
print(res)

