# TravellingSalespersonProblem

The [travelling salesperson problem](https://en.wikipedia.org/wiki/Travelling_salesman_problem) is a np-hard problem with application in supply chain and computer science. The below code uses PuLP solver to find the exact solution of the TSP. Other dependencies include numpy and pandas.

The mathematical formulation is summarrised below:

## Sets and Decision variables

$\mathbb{N}$ is the set of all customer node subset $i$ and $j$

We will use  binary variable $x_{ij}$ 

$x_{ij}$ will take the value 1 if truck travels from node $i$ to node $j$, 0 otherwise. $i\in\mathbb{N}$ and $j\in\mathbb{N}$

Other variables are:

$u_{i}$ will take the value of the order of node $i$ in the final route of truck. $i\in\mathbb{N}^{}$

$t_{i}$ represents the arrival time for truck at node $i$. 

$tt_{ij}$ represents the truck travel time between nodes $i$ and $j$. 

$M$ is a very large number

Objective: Minimize the total time to visit all nodes

$$ Obj=min\{\sum_{i=D}^{D'}t_{i}\} $$

Constraint 1: All nodes have to be visited by truck exactly once

$$ \sum_{i=D}^{D'}x_{ij}=1 $$

Constraint 2: Truck leaves depot D and comes back to depot D' exactly once $i=D,D'$

$$ \sum_{j=D}^{n}x_{ij}=1 $$ 

$$ \sum_{j=D}^{D'}x_{jk}=1 $$

Constraint 3: If truck arrives at node j then it should also leave node j.

$$ \sum_{i=D}^{D'}x_{ij}=\sum_{k=D}^{D'}x_{jk} for j\in\mathbb{N} $$

Constraint 4: Avoiding sub-tours for truck

$$ u_{j}-u_{k}-1\leq M(1-x_{jk}) $$

Constraint 5: We will add travel time $tt_{ij}$ to arrival time at node $i$ to get arrival time at node $j$ if truck travels in $ij$ path

$$ t_{j}\geq t_{i}+tt_{ij}-M(1-x_{ij}) $$

Input Parameters:

**_time_matrix_**: is a **_NxN_** cost matrix between the points that have to be visited by the nodes, example:

```
    0     1   2     3   4
0   0  21.0  15  21.0  10
1  21   0.0   5   0.5  11
2  15   5.0   0   5.0   5
3  21   0.5   5   0.0  10
4  10  11.0   5  10.0   0
```

For small instances with $\leq15$ nodes, the tsp_exact function will give the exact solution. For instances $> 15$ nodes, heuristic solutions are preferred due to high computation time. (Remember, tsp is a NP-hard problem with O(2!))

We define the following heuristics for tsp:

1. Nearest neighbor heuristics: The nearest node to the tour is added to the tour
2. Nearest insertion heuristics: The nearest node to the tour is inserted in the tour at an arc with minimum cost
3. Cheapest insertion heuristics: Modified version of Nearest insertion heuristics which checks all nodes for insertion instead of the nearest node
4. Farthest insertion heuristics:  The farthest node to the tour is inserted in the tour at an arc with minimum cost
5. MST heuristics: Minimum spanning tree is created for the network and repeated nodes are removed to form the route

## Example 1:

<img src=https://user-images.githubusercontent.com/114884444/198330529-16e2fe72-fbd9-4b71-93a6-2dbaafee60e2.png width="400">

With the below distance matrix:
```
time_matrix=
0	1	2	3	4	5	6	7	8
0	14.015	14.411	14.749	21.253	19.333	9.37	10.186	15.054
14.003	0	5.317	30.438	9.109	16.033	6.13	5.209	5.062
14.022	5.251	0	30.411	6.656	14.415	8.705	4.708	1.047
14.755	30.741	30.746	0	37.979	21.296	26.096	26.521	31.389
21.384	8.819	5.854	37.818	0	21.869	14.803	25.428	6.925
18.62	16.179	15.038	21.287	21.128	0	23.369	10.812	15.68
9.89	5.853	8.274	26.325	14.396	23.082	0	13.935	8.031
9.987	5.599	4.458	26.377	10.709	10.938	7.619	0	5.1
15.122	6.061	1.372	31.512	7.284	15.516	8.907	5.354	0

tsp_exact(time_matrix)
```

## Output:
<img src=https://user-images.githubusercontent.com/114884444/198332900-cd10d859-a6d4-42d2-816a-bf771b08cbc6.png width='400'>



