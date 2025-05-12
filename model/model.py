from datetime import datetime
from database.DAO import DAO
import networkx as nx
import geopy.distance


class Model:
    def __init__(self):
        self._fermate = DAO.getAllFermate()
        self._grafo = nx.DiGraph()  # creo il grafo privato nel costruttore del modello, lo creo una volta e bom
        self._idMapFermate = {}
        for f in self._fermate:
            self._idMapFermate[f.id_fermata] = f  # creo una mappa che mi collega l'id alla fermata

    # per costruire il grafo
    def buildGraph(self):
        # aggiungiamo i nodi
        self._grafo.add_nodes_from(self._fermate)  # creo i nodi partendo dalla lista di fermate prese dal DAO

        # tic = datetime.now()
        # self.addEdges1()
        # toc = datetime.now()
        # print("Tempo modo 1:", (toc-tic))

        # self._grafo.clear_edges()
        # tic = datetime.now()
        # self.addEdges2()
        # toc = datetime.now()
        # print("Tempo modo 2:", (toc - tic))

        # self._grafo.clear_edges()
        tic = datetime.now()
        self.addEdges3()
        toc = datetime.now()
        print("Tempo modo 3:", (toc - tic))

    def addEdges1(self):  # ci mette troppo tempo perchè itera n * n volte, con n numero di nodi
        """
        Aggiungo gli archi con doppio ciclo sui nodi,
        e testando se per ogni coppia esiste una connessione
        """
        for u in self._fermate:
            for v in self._fermate:
                if DAO.hasConnessione(u, v):
                    self._grafo.add_edge(u, v)
                    # print("Aggiungo arco fra", u, "e", v)

    def addEdges2(self):
        """
        Ciclo solo una volta e faccio una query per trovare tutti i vicini
        """
        for u in self._fermate:
            for con in DAO.getVicini(u):
                v = self._idMapFermate[con.id_stazA]  # accedo alla fermata tramite l'id inserito come chiave nella mappa
                self._grafo.add_edge(u, v)

    def addEdges3(self):
        """
        faccio una query unica che prende tutti gli archi e poi ciclo qui
        """
        allEdges = DAO.getAllEdges()
        for edge in allEdges:
            u = self._idMapFermate[edge.id_stazP]  # accedo alla fermata tramite l'id inserito come chiave nella mappa
            v = self._idMapFermate[edge.id_stazA]
            self._grafo.add_edge(u, v)

    def getNumNodi(self):
        return len(self._grafo.nodes)

    def getNumArchi(self):
        return len(self._grafo.edges)

    # visita del grafo
    def getBFSNodesFromTree(self, source):  # visita in ampiezza, source è la fermata di partenza che inserisce l'utente
        tree = nx.bfs_tree(self._grafo, source)  # ritorna un albero orientato costruito a partire da source
        archi = tree.edges
        nodi = list(tree.nodes)
        return nodi[1:]  # escludo la source

    def getDFSNodesFromTree(self, source):  # visita in profondità
        tree = nx.dfs_tree(self._grafo, source)
        nodi = list(tree.nodes)
        return nodi[1:]  # escludo la source

    def getBFSNodesFromEdges(self, source):
        archi = nx.bfs_edges(self._grafo, source)  # mi restituisce direttamente gli archi ottenuto attraverso il metodo bfs
        res = []
        for u, v in archi:
            res.append(
                v)  # aggiungo il secondo elemento della tupla per prendere solo i nodi di arrivo dei vari archi, questo mi genera il cammino della ricerca BFS
        return res

    def getDFSNodesFromEdges(self, source):
        archi = nx.dfs_edges(self._grafo,
                             source)  # mi restituisce direttamente gli archi ottenuto attraverso il metodo dfs
        res = []
        for u, v in archi:
            res.append(v)
        return res

    # per le estensioni
    def buildGraphPesato(self):
        self._grafo.clear()  # pulisco il grafo perchè stiamo usando lo stesso creato senza considerare i pesi
        self._grafo.add_nodes_from(self._fermate)  # riempio i nodi del grafo con le fermate salvate dal DAO
        # self.addEdgesPesatiV2()
        self.addEdgesPesatiTempi()  # per i cammini minimi

    def addEdgesPesati(self):
        allEdges = DAO.getAllEdges()
        for edge in allEdges:
            u = self._idMapFermate[
                edge.id_stazP]  # accedo alla fermata tramite l'id inserito come chiave nella mappa
            v = self._idMapFermate[edge.id_stazA]

            if self._grafo.has_edge(u, v):  # metodo che restituisce True se l'arco appartiene al grafo
                self._grafo[u][v][
                    "weight"] += 1  # aumento di 1 il peso dell'arco, ogni volta che trovo una linea tra quelle due fermate
            else:
                self._grafo.add_edge(u, v,
                                     weight=1)  # se non trovo l'arco, allora lo aggiungo e gli associo il peso 1

    def addEdgesPesatiV2(self):
        self._grafo.clear_edges()
        allEdgesPesati = DAO.getAllEdgesPesati()

        for e in allEdgesPesati:
            self._grafo.add_edge(self._idMapFermate[e[0]], self._idMapFermate[e[1]],
                                 weight=e[2])  # il peso diventa il count della query fatta nel DAO

    def getArchiPesoMaggiore(self):
        edges = self._grafo.edges(data=True)
        res = []
        for e in edges:
            if self._grafo.get_edge_data(e[0], e[1])["weight"] > 1:  # trovo gli archi con peso maggiore di 1, quindi con più di una linea che collega le due fermate
                res.append(e)
        return res

    # per i cammini minimi
    def addEdgesPesatiTempi(self):
        """
        aggiunge archi con peso uguale al tempo di percorrenza dell'arco
        """
        self._grafo.clear_edges()
        allEdges = DAO.getAllEdgesVel()
        for e in allEdges:  # e è una tupla di tre elementi: id_StazP, id_StazA, velocità dell'arco
            u = self._idMapFermate[e[0]]  # il primo elemento della tupla, accedo alla stazione di partenza con l'idMap
            v = self._idMapFermate[e[1]]  # stazione di arrivo
            peso = getTraversalTime(u, v, e[2])  # e[2] è la velocità
            self._grafo.add_edge(u, v, weight=peso)

    # per i cammini minimi
    def getShortestPath(self, u, v):
        return nx.single_source_dijkstra(self._grafo, u, v)  # restituisce distanza e percorso, come lista di nodi


    @property
    def fermate(self):
        return self._fermate


def getTraversalTime(u, v, vel):  # uso di libreria geopy per trovare le distanze
    dist = geopy.distance.distance((u.coordX, u.coordY), (v.coordX, v.coordY)).km  # passo come argomenti due tuple con le rispettive coordinate dei due nodi
    # mi restituisce la distanza in chilometri
    time = dist / vel * 60  # mi restituisce il tempo in minuti
    return time  # calcola il tempo di percorrenza di un arco dati due punti e la relativa velocità
