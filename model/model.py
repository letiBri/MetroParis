from datetime import datetime

from database.DAO import DAO
import networkx as nx

class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo = nx.DiGraph()  # creo il grafo privato nel costruttore del modello, lo creo una volta e bom
        self._idMapFermate = {}
        for f in self._fermate:
            self._idMapFermate[f.id_fermata] = f  # creo una mappa che mi collega l'id alla fermata

    def buildGraph(self):
        # aggiungiamo i nodi
        self._grafo.add_nodes_from(self._fermate)  # creo i nodi partendo dalla lista di fermate prese dal DAO

        # tic = datetime.now()
        # self.addEdges1()
        # toc = datetime.now()

        # tic = datetime.now()
        # self.addEdges2()
        # toc = datetime.now()

        tic = datetime.now()
        self.addEdges3()
        toc = datetime.now()


    def addEdges1(self): # ci mette troppo tempo perche itera n * n volte, con n numero di nodi
        """ Aggiungo gli archi con doppio ciclo sui nodi
        e testando se per ogni coppia esiste una connessione"""
        for u in self._fermate:
            for v in self._fermate:
                if DAO.hasConnessione(u, v):
                    self._grafo.add_edge(u, v)
                    print("Aggiungo arco fra", u, "e", v)

    def addEdges2(self):
        """
        Ciclo solo una volta e faccio una query per trovare tutti i vicini
        """
        for u in self._fermate:
            for con in DAO.getVicini(u):
                v = self._idMapFermate[con.id_stazA]
                self._grafo.add_edge(u, v)


    def addEdges3(self):
        """
        faccio una query unica che prende tutti gli archi e poi ciclo qui
        """
        allEdges = DAO.getAllEdges()
        for edge in allEdges:
            u = self._idMapFermate[edge.id_stazP]
            v = self._idMapFermate[edge.id_stazA]
            self._grafo.add_edge(u, v)


    def getNumNodi(self):
        return len(self._grafo.nodes)

    def getNumArchi(self):
        return len(self._grafo.edges)

    @property
    def fermate(self):
        return self._fermate

