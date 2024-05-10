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

from pyscipopt import Model


def read_data_from_model(model):
    """
    :param model: model provided by gurobi
    :return:
    """
    model.optimize()                                #stuck in here

    variables = model.getVars()
    for var in variables[:10]:
        print(f'Variable Name: {var.name}, Objective Coefficient: {model.getObjCoef(var)} LB: {var.getLb()}, UB: {var.getUb()}')



    constraints = model.getConstrs()
    for constraint in constraints[:10]:
        print(f'Constraint Name: {constraint.name}, RHS: {model.getRhs(constraint)}')
        #print(f'Constraint Name: {constr.constrName}, Sense: {constr.sense}')
        cons_expr = model.getConsExpr(constraint)
        print(f'Constraint Expression: {cons_expr}')

    objective = model.getObjective()
    print(f'Objective: {objective}')

def get_miplib_data(path,path_extract):
    """
    path_extract:data/extract/bm
    测试用路径：data/benchmark.zip
    :param path: 文件路径
    :return:
    """
    zip_path = path
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path=path_extract)

    extracted_folder = path_extract
    for filename in os.listdir(extracted_folder):
        if filename.endswith(".mps.gz"):
            gz_file_path = os.path.join(extracted_folder, filename)
            temp_uncompressed_path = os.path.join(extracted_folder, filename[:-3])

            with gzip.open(gz_file_path, 'rb') as gz_file:
                with open(temp_uncompressed_path, 'wb') as uncompressed_file:
                    uncompressed_file.write(gz_file.read())

            # 使用PuLP读取MPS文件
            model = Model()
            model.readProblem(temp_uncompressed_path)

            #从model中提取数据
            read_data_from_model(model)
            break

            # 这里可以添加你的处理逻辑
            # 例如：problem.solve()

            print(f"Processed {filename}")

            os.remove(temp_uncompressed_path)



get_miplib_data("data/benchmark.zip","data/extract/bm")