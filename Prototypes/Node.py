class Node:

    #Class node defines the properties of a node(Port) and creates the
    #list for each nodes' neighbours.

    def __init__(self, Name):
        self.E_name = Name
        self.pred = None
        self.dist = 999999
        self.neighbours = []

    def add_n(self, *args):
        for index in args:
            if index not in self.neighbours:
                self.neighbours.append(index)

    def get_n(self):
        return self.neighbours
