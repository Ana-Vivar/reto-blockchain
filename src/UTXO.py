
class UTXO:
    """
    Clase que representa un UTXO (Unspent Transaction Output) en la red de blockchain.
    Parámetros:
        propietario: Dirección del propietario del UTXO.
        cantidad: Cantidad de monedas asociadas al UTXO.
        txid: Identificador de la transacción a la que pertenece el UTXO.
    Métodos:
        generar_dict: Genera un diccionario con los atributos del UTXO.
    """
    def __init__(self, txid, propietario, cantidad):

        self.txid = txid
        self.propietario = propietario.direccion
        self.cantidad = cantidad
        
    def generar_dict(self):
        """Genera un diccionario con los atributos del UTXO."""
        return {"txid": self.txid, "direccion": self.propietario,"cantidad": self.cantidad}
        