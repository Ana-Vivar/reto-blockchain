from hashlib import sha256
from datetime import datetime
import json

class Bloque:
    """
    Clase que representa un bloque en la cadena de bloques.
    Parámetros:
        idx: Índice del bloque, utilizado para identificarlo de manera única.
        transacciones: Lista de transacciones incluidas en el bloque.
        previous_hash: Hash del bloque anterior, utilizado para enlazar los bloques.
        
    Métodos:
        crear_dict: Crea un diccionario con los atributos del bloque.
        calcular_hash: Calcula el hash del bloque utilizando sus atributos.
    """
    def __init__(self, idx, transacciones, previous_hash):

        self.idx = idx
        self.timestamp = str(datetime.now())
        self.transacciones = transacciones
        self.previous_hash = previous_hash
        self.nonce = 0
        self.tiempo_minado = None
        self.recompensa = None
        self.hash = self.calcular_hash()


    def crear_dict(self):
        """
        Crea un diccionario con los atributos del bloque.
        """
        bloque_dict = {
            "idx": self.idx,
            "timestamp": self.timestamp,
            "transacciones": self.transacciones,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "tiempo_minado": self.tiempo_minado,
            "recompensa": self.recompensa,
            
        }
        return bloque_dict

    def calcular_hash(self):
        """
        Calcula el hash del bloque utilizando sus atributos.
        """
        bloque_data = self.crear_dict()
        bloque_data_str = json.dumps(bloque_data, sort_keys=True)

        return sha256(bloque_data_str.encode()).hexdigest()