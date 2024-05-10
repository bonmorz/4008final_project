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

import numpy as np

from pyscipopt import Model, quicksum, SCIP_RESULT, SCIP_PARAMSETTING,SCIP_EVENTTYPE,Eventhdlr


# read the path to a problem and get the answer of the
def collect_every_solution(path):
    model = Model()
    model.readProblem(path)

    model.setParam('limits/time', 600)


    # Disable presolving and enable solution collection
    model.setPresolve(SCIP_PARAMSETTING.OFF)

    # model.setParam('limits/solutions', -1)  # Collect all solutions

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
            # sol = self.model.getBestSol()
            # x_val = self.model.getVars()

            # self.solutions.append(x_val)

            sol = self.model.getBestSol()
            sol_values = {var.name: self.model.getSolVal(sol, var) for var in self.model.getVars()}
            self.solutions.append(sol_values)

    # Create an instance of the event handler
    solution_collector = SolutionCollector()

    # Include the event handler in the model
    model.includeEventhdlr(solution_collector, "SolutionCollector", "Collects all feasible solutions")

    # Solve the model
    model.optimize()

    sol_set = solution_collector.solutions

    # 现在我们拥有了路径中问题的所有可行解的集合，可以用它来构建二部图了

    return sol_set


problem_file_path = 'data/extract/bm_ex'
solution_file_path = 'data/extract/bm_ex_solution'


def get_solution_from_file(path):
    # 确保解决方案文件夹存在
    if not os.path.exists(solution_file_path):
        os.makedirs(solution_file_path)

    for filename in os.listdir(path):
        print(filename)
        # 移除原有的扩展名，并为目标文件添加.txt扩展名
        base_filename, _ = os.path.splitext(filename)
        solution_filename = base_filename + '.txt'

        # 构造可能存在的解决方案文件的完整路径
        possible_solution_file = os.path.join(solution_file_path, solution_filename)

        # 检查解决方案文件是否已经存在
        if os.path.exists(possible_solution_file):
            print(f"Solution file {solution_filename} already exists. Skipping...")
            continue  # 如果存在，跳过当前循环

        # 构造原始文件的完整路径
        file_path = os.path.join(path, filename)
        # 调用函数获取解决方案数组
        file_ans = collect_every_solution(file_path)

        # 使用新的解决方案文件名构造解决方案文件的完整路径
        solution_file = os.path.join(solution_file_path, solution_filename)

        # 打开文件进行写入
        with open(solution_file, 'w') as f:
            for item in file_ans:
                # 将数组中的每个元素转换为字符串并写入文件
                f.write(str(item) + '\n')


get_solution_from_file(problem_file_path)