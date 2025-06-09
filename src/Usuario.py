from hashlib import sha256
from ecdsa import SECP256k1, SigningKey, BadSignatureError

class Usuario:
    """
    Clase que representa a un usuario en la red de blockchain.
    Parametros:
        idx: Índice del usuario, utilizado para identificarlo de manera única.
        sign_key: Llave privada del usuario, utilizada para firmar transacciones.
        key: Llave pública del usuario, utilizada para verificar firmas.
        llave_privada: Representación hexadecimal de la llave privada.
        llave_publica: Representación hexadecimal de la llave pública.
        direccion: Dirección del usuario, generada a partir de la llave pública.
    Métodos:
        crear_llaves: Genera las llaves privada y pública del usuario.
        generar_dir: Genera la dirección del usuario a partir de su llave pública.
        firmar: Firma un mensaje con la llave privada del usuario.
        checar_cartera: Checa la cantidad de monedas en el conjunto de UTXOs del usuario.
        verificar_firma: Verifica la firma de un mensaje con la llave pública del usuario.
    """
    def __init__(self, idx):
        
        self.idx = idx
        self.sign_key = SigningKey.generate(curve=SECP256k1)
        self.key = self.sign_key.get_verifying_key()
        self.llave_privada, self.llave_publica =self.crear_llaves()
        self.direccion = self.generar_direccion()

    def crear_llaves(self):
        """Genera las llaves privada y pública del usuario."""
        llave_privada = self.sign_key.to_string().hex()
        llave_publica = self.key.to_string().hex()

        return llave_privada, llave_publica
    
    def generar_direccion(self):
        """Genera la dirección del usuario a partir de su llave pública."""
        return sha256(self.key.to_string()).hexdigest()
    
    def firmar(self, mensaje):
        """Firma un mensaje con la llave privada del usuario."""
        return self.sign_key.sign(mensaje.encode(), hashfunc=sha256)
    
    def verificar_firma(self, mensaje, firma):
        """Verifica la firma de un mensaje con la llave pública del usuario."""
        try:
            return self.key.verify(firma, mensaje.encode(), hashfunc=sha256)
        except BadSignatureError:
            return False

    def checar_cartera(self, UTXOs_set):
        """Checa la cantidad de monedas en el conjunto de UTXOs del usuario."""
        return sum(utxo.cantidad for utxo in UTXOs_set if utxo.propietario == self.direccion)
    
    def crear_dict(self):
        """Genera un diccionario con los atributos del usuario."""
        dict_usuario = {
            "idx": self.idx,
            "llave_privada": self.llave_privada,
            "llave_publica": self.llave_publica,
            "direccion": self.direccion
        }
        return dict_usuario