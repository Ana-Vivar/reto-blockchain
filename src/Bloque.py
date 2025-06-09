from hashlib import sha256
from datetime import datetime
import json

class Bloque:
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