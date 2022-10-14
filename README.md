# TravellingSalesmanProblem

The [travelling salesman problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem) is a np-hard problem with application in supply chain and computer science. The below code uses PuLP solver to find the exact solution of the TSP. Other dependencies include numpy and pandas.

Input Parameters:

**_time_matrix_**: is a **_NxN_** cost matrix between the points example:

```
    0     1   2     3   4
0   0  21.0  15  21.0  10
1  21   0.0   5   0.5  11
2  15   5.0   0   5.0   5
3  21   0.5   5   0.0  10
4  10  11.0   5  10.0   0
```

## Example 1:

```
time_matrix = pd.DataFrame({0:[0,21,15,21,10],
                           1:[21,0,5,.5,11],
                           2:[15,5,0,5,5],
                           3:[21,0.5,5,0,10],
                           4:[10,11,5,10,0]})

TSP_truck(time_matrix)
```

## Output:

```
status: 1, Optimal
objective: 65.5
decisionVariable_T_1: 20.5
decisionVariable_T_2: 15.0
decisionVariable_T_3: 20.0
decisionVariable_T_4: 10.0
decisionVariable_U_1: 4.0
decisionVariable_U_2: 2.0
decisionVariable_U_3: 3.0
decisionVariable_U_4: 1.0
decisionVariable_X_(0,_4): 1.0
decisionVariable_X_(1,_0): 1.0
decisionVariable_X_(2,_3): 1.0
decisionVariable_X_(3,_1): 1.0
decisionVariable_X_(4,_2): 1.0
```


