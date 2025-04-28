from model.model import Model

model = Model()
model.buildGraph()
print("Num nodi: ", model.getNumNodi())
print("Num archi: ", model.getNumArchi())
