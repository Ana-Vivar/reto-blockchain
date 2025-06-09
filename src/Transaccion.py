from hashlib import sha256
import json

from src.UTXO import UTXO

class Transaccion:
    """Clase que representa una transacción en la red de blockchain.
        Parámetros:
            idx: Índice de la transacción, utilizado para identificarla de manera única.
            sistema: Sistema de blockchain al que pertenece la transacción, contiene el conjunto de UTXOs.
            emisor: Usuario que envía la transacción, None si es una transacción coinbase.
            receptor: Usuario que recibe la transacción, se le asignará un nuevo UTXO.
            dir_emisor: Dirección del emisor, se obtiene del usuario.
            dir_receptor: Dirección del receptor, se obtiene del usuario.
            mining_fee: Tarifa de minería, se suma al total de la transacción.
            cantidad: Cantidad de monedas que se transfieren en la transacción.
            UTXOs_set: Conjunto de UTXOs del sistema, utilizado para verificar y actualizar los UTXOs.
        Métodos:
            lista_UTXO_emisor: Crea una lista de UTXOs del emisor.
            verificar_tx: Verifica si la transacción es válida.
            seleccionar_utxos: Selecciona los UTXOs necesarios para cubrir la cantidad de la transacción.
            crear_txid: Crea un identificador único para la transacción.
            firmar_tx: Firma la transacción con la llave privada del emisor.
            verificar_firma: Verifica la firma de la transacción con la llave pública del emisor.
            validar_y_preparar_tx: Valida la transacción y la prepara para enviar a la mempool (sin tocar UTXOs_set).
            aplicar_tx: Aplica los cambios en el UTXOs_set (se llama solo cuando la tx se mina).
            hacer_tx: Realiza la transacción, actualizando el sistema y los UTXOs (solo se utiliza para crear el bloque genesis).
            crear_dict: Crea un diccionario con los atributos de la transacción.
    """
    def __init__(self, idx, emisor, receptor, cantidad, sistema):

        self.idx = idx
        self.sistema = sistema
        self.emisor = emisor
        self.receptor = receptor
        self.dir_receptor = receptor.direccion
        self.mining_fee = sistema.mining_fee

        if emisor is None:
            self.dir_emisor = None
            self.cantidad = cantidad
        else:
            self.dir_emisor = emisor.direccion
            self.cantidad = cantidad

        self.UTXOs_set = sistema.UTXOs_set
        
        self.UTXO_emisor = []
        self.UTXO_seleccionados = []
        self.total_seleccionado = 0
        self.txid = None
        self.firma = None

    def lista_UTXO_emisor(self):
        """Crea una lista de UTXOs del emisor."""
        self.UTXO_emisor = [utxo for utxo in self.UTXOs_set if utxo.propietario == self.dir_emisor]
    
    def verificar_tx(self):
        """Verifica si la transacción es válida."""

        total_credito = sum(utxo.cantidad for utxo in self.UTXO_emisor)
        
        if total_credito < self.cantidad + self.mining_fee:
            print('Transacción invalida: no hay saldo suficiente.')
            return False
        else:
            return True

    def seleccionar_utxos(self):
        """Selecciona los UTXOs necesarios para cubrir la cantidad de la transacción."""
        utxo_seleccionados = []
        utxo_emisor = sorted(self.UTXO_emisor, key=lambda x: x.cantidad + self.mining_fee)
        total = 0

        for utxo in utxo_emisor:
            utxo_seleccionados.append(utxo)
            total += utxo.cantidad
            if total >= self.cantidad + self.mining_fee:
                break
        if total < self.cantidad + self.mining_fee:
            print("Error: saldo insuficiente después de seleccionar UTXOs.")
            return False
            
        self.UTXO_seleccionados = utxo_seleccionados
        self.total_seleccionado = total
        return True

    def crear_txid(self):
        """Crea un identificador único para la transacción."""
        utxos_info = [utxo.generar_dict() for utxo in self.UTXO_seleccionados]

        tx_data = {
            "idx": self.idx,
            "emisor": self.dir_emisor,
            "receptor": self.dir_receptor,
            "cantidad": self.cantidad,
            "UTXOs_emisor": utxos_info
        }
        tx_data_str = json.dumps(tx_data, sort_keys=True)

        return sha256(tx_data_str.encode()).hexdigest()

    def firmar_tx(self):
        """Firma la transacción con la llave privada del emisor."""
        if self.emisor is not None:
            self.firma = self.emisor.firmar(self.txid)
    
    def verificar_firma(self):
        """Verifica la firma de la transacción con la llave pública del emisor."""
        if self.emisor is None:
            return True
        return self.emisor.verificar_firma(self.txid, self.firma)

    def validar_y_preparar_tx(self):
        """Valida la transacción y la prepara para enviar a la mempool (sin tocar UTXOs_set)."""
        if self.emisor is None:
            self.txid = self.crear_txid()
            self.firmar_tx()
            return self.crear_dict()

        self.lista_UTXO_emisor()
        if not self.verificar_tx():
            return None

        if not self.seleccionar_utxos():
            return None

        self.txid = self.crear_txid()
        self.firmar_tx()

        if not self.verificar_firma():
            print("Error: firma inválida.")
            return None

        return self.crear_dict()

    def aplicar_tx(self):
        """Aplica los cambios en el UTXOs_set (se llama solo cuando la tx se mina)."""
        if self.emisor is None:
            utxo_receptor = UTXO(self.txid, self.receptor, self.cantidad)
            self.UTXOs_set.append(utxo_receptor)
            return

        for utxo in self.UTXO_seleccionados:
            self.UTXOs_set.remove(utxo)

        utxo_receptor = UTXO(self.txid, self.receptor, self.cantidad)
        self.UTXOs_set.append(utxo_receptor)

        cambio = self.total_seleccionado - self.cantidad
        if cambio > 0:
            utxo_cambio = UTXO(self.txid, self.emisor, cambio)
            self.UTXOs_set.append(utxo_cambio)

        self.sistema.fees.append(self.mining_fee)

    def hacer_tx(self):
        """Realiza la transacción, actualizando el sistema y los UTXOs."""
            
        if self.emisor is None:
            self.txid = self.crear_txid()
            utxo_receptor = UTXO(self.txid, self.receptor, self.cantidad)
            self.UTXOs_set.append(utxo_receptor)
            self.firmar_tx()
            return True
    
    def crear_dict(self):
        """Crea un diccionario con los atributos de la transacción."""

        utxos_info = [utxo.generar_dict() for utxo in self.UTXO_seleccionados]

        tx_dict = {
            "idx": self.idx,
            "txid": self.txid,
            "emisor": self.dir_emisor,
            "receptor": self.dir_receptor,
            "cantidad": self.cantidad,
            "mining_fee": self.mining_fee,
            "UTXOs_emisor": utxos_info,
            "firma": self.firma.hex() if self.firma else None
        }

        return tx_dict