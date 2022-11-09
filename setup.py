from setuptools import setup 

setup(name = 'tsp_solutions',
version='0.0.1',
description='The travelling salesman problem is a np-hard problem with application in supply chain and computer science',
long_description='''
 The code uses PuLP module to formulate the problem and CPLEX, GUROBI, COIN_CMD, and PULP_solver to find the exact solution of the TSP. 
 The module also includes heuristics and metaheuristics functions that can be used for large instances.
 More functions will be added.
 If you find an error or want to solve problems together write to me @shamikpushkar92@gmail.com.
 
 Dependencies include pulp, numpy, pandas, scipy, and copy.
''',
author='Shamik Pushkar',
author_email='shamikpushkar92@gmail.com',
url = 'https://github.com/projektdexter/tsp',
packages=['tsp_solutions'],
install_requires=['numpy','pandas','pulp','scipy'],
keywords=['python', 'travelling-salesman-problem', 'combinatorial-optimization', 'linear-programming', 'integer-programming', 'pulp', 'optimization', 'heuristics','metaheuristics','vrp','vehicle-routing-problem']
)