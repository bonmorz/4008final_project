import zipfile
from pulp import LpProblem
import os
import gzip
from gurobipy import read, GRB

import graph_nets as gn
import sonnet as snt
import tensorflow as tf
from graph_nets import graphs
from graph_nets import utils_tf

from pyscipopt import Model, quicksum, SCIP_RESULT, SCIP_PARAMSETTING,SCIP_EVENTTYPE,Eventhdlr

temp_path = 'data/extract/testproblem/10teams.mps'




def collect_every_solution(path):
    model = Model()
    model.readProblem(path)

    # Disable presolving and enable solution collection
    model.setPresolve(SCIP_PARAMSETTING.OFF)
    #model.setParam('limits/solutions', -1)  # Collect all solutions



    class SolutionCollector(Eventhdlr):
        def __init__(self):
            super().__init__()
            self.model = model
            self.solutions = []

        def eventinit(self):
            self.model.catchEvent(SCIP_EVENTTYPE.BESTSOLFOUND, self)

        def eventexit(self):
            self.model.dropEvent(SCIP_EVENTTYPE.BESTSOLFOUND, self)

        def eventexec(self, event):
            sol = self.model.getBestSol()
            x_val = self.model.getVars()

            self.solutions.append(x_val)

    # Create an instance of the event handler
    solution_collector = SolutionCollector()

    # Include the event handler in the model
    model.includeEventhdlr(solution_collector, "SolutionCollector", "Collects all feasible solutions")

    # Solve the model
    model.optimize()


    sol_set = solution_collector.solutions

    #现在我们拥有了路径中问题的所有可行解的集合，可以用它来构建二部图了


    return sol_set



ans = collect_every_solution(temp_path)

print(len(ans))