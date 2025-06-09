import time
from src.Usuario import Usuario
from src.UTXO import UTXO
from src.Transaccion import Transaccion
from src.Bloque import Bloque

class Sistema:
    """Clase que representa el sistema de blockchain.
    Contiene la lógica para manejar usuarios, transacciones, bloques y minería.
    Parámetros:
        dificultad: Dificultad de minería.
        mining_reward: Recompensa por minar un bloque.
        mining_fee: Tarifa de minería por transacción.
        usuarios: Lista de usuarios registrados en el sistema.
        blockchain: Lista que representa la cadena de bloques.
        UTXOs_set: Conjunto de UTXOs disponibles en el sistema.
        transacciones: Lista de transacciones realizadas en el sistema.
        mempool: Lista de transacciones pendientes de ser minadas.
        recompensas: Lista de recompensas obtenidas por minar bloques.
        fees: Lista de tarifas de minería acumuladas.
        idx_usuario: Índice para identificar usuarios de manera única.
        idx_tx: Índice para identificar transacciones de manera única.
        idx_bloque: Índice para identificar bloques de manera única.
        idx_utxo: Índice para identificar UTXOs de manera única.
    Métodos:
        agregar_usuario: Agrega un nuevo usuario al sistema.
        crear_usuario: Crea un nuevo usuario y lo agrega al sistema.
        agregar_bloque: Agrega un bloque a la cadena de bloques.
        get_utxo_idx: Genera un identificador único para un UTXO.
        agregar_tx: Agrega una transacción al sistema.
        procesar_tx: Procesa una transacción entre un emisor y un receptor.
        get_cartera: Devuelve un diccionario con las direcciones de los usuarios y sus saldos.
        crear_coinbase_tx: Crea una transacción de coinbase para el minero.
        get_mining_fees: Calcula las tarifas de minería acumuladas en la mempool.
        minar_bloque: Minera un bloque y lo agrega a la cadena de bloques.
        crear_bloque_genesis: Crea el bloque génesis y el usuario génesis.
    """
    
    def __init__(self, dificultad=4):

        # Minado
        self.dificultad = dificultad
        self.mining_reward = 3
        self.mining_fee = 0.1
        
        self.usuarios = []
        self.blockchain = []
        self.UTXOs_set = []
        self.transacciones = []
        self.mempool = []               # transacciones pendientes
        self.recompensas = []
        self.fees = []

        # Índices
        self.idx_usuario = 0
        self.idx_tx = 0
        self.idx_bloque = 0
        self.idx_utxo = 0
        self.primer_usuario = self.crear_bloque_genesis()


    def agregar_usuario(self, usuario):
        """
        Agrega un usuario al sistema.
        """
        self.usuarios.append(usuario)

    def crear_usuario(self):
        """
        Crea un nuevo usuario y lo agrega al sistema.
        """
        nuevo_usuario = Usuario(self.idx_usuario)
        self.agregar_usuario(nuevo_usuario)
        self.idx_usuario += 1
        print(f"Usuario creado: {nuevo_usuario.direccion}")

        return nuevo_usuario
    
    def agregar_bloque(self, bloque):
        """
        Agrega un bloque a la cadena de bloques.
        """
        self.blockchain.append(bloque)
        self.idx_bloque += 1
        print(f"Bloque {bloque.idx} agregado a la cadena de bloques.")
    
    def get_utxo_idx(self):
        """
        Genera un identificador único para un UTXO.
        """
        utxo_idx = self.idx_utxo
        self.idx_utxo += 1
        return str(utxo_idx)
    
    def agregar_tx(self, transaccion):
        """Agrega una transacción al sistema.
        """
        self.transacciones.append(transaccion)

        if transaccion.emisor is None:
            print("Transacción de coinbase agregada al sistema.")
        else:
            print(f"Transacción de {transaccion.emisor.direccion} a {transaccion.receptor.direccion} por {transaccion.cantidad} agregada al sistema.")
    
    def procesar_tx(self, sender, receiver, amount):
        
        transaccion = Transaccion(
            idx=self.idx_tx,
            emisor=sender,
            receptor=receiver,
            cantidad=amount,
            sistema=self,
        )
        tx_dict = transaccion.validar_y_preparar_tx()

        if tx_dict:
            self.agregar_tx(transaccion)
            self.mempool.append({
                "tx_obj": transaccion,
                "tx_dict": tx_dict,
            })
            self.idx_tx += 1
            print(f"Transacción {transaccion.txid} procesada y agregada a la mempool.")
            return True
        else:
            print("Error al procesar la transacción.")
            return False

    
    def get_cartera(self):
        """
        Devuelve un diccionario con las direcciones de los usuarios y sus saldos.
        """
        cartera = {}
        for usuario in self.usuarios:
            saldo = usuario.checar_cartera(self.UTXOs_set)
            cartera[f'Usuario {usuario.idx}'] = [usuario.direccion, saldo]
        return cartera
    
    def crear_coinbase_tx(self, minero, cantidad):
        """
        Crea una transacción de coinbase para el minero.
        """
        coinbase_tx = Transaccion(
            idx=self.idx_tx,
            emisor=None,
            receptor=minero,
            cantidad=cantidad,
            sistema=self,
        )
        return coinbase_tx
    
    def get_mining_fees(self):
        total = sum(tx["tx_dict"]["mining_fee"] for tx in self.mempool if tx["tx_dict"]["emisor"] is not None)
        return total

    def minar_bloque(self, minero):
        cantidad_coinbase = self.mining_reward + self.get_mining_fees()
        coinbase_tx = self.crear_coinbase_tx(minero, cantidad_coinbase)
        coinbase_tx.validar_y_preparar_tx()

        transacciones_bloque = [coinbase_tx.crear_dict()] + [tx["tx_dict"] for tx in self.mempool]

        bloque_anterior = self.blockchain[-1]
        hash_anterior = bloque_anterior.hash
        idx_bloque = self.idx_bloque

        nuevo_bloque = Bloque(
            idx=idx_bloque,
            transacciones=transacciones_bloque,
            previous_hash=hash_anterior
        )

        start_time = time.time()

        while not nuevo_bloque.hash.startswith('0' * self.dificultad):
            nuevo_bloque.nonce += 1
            nuevo_bloque.hash = nuevo_bloque.calcular_hash()

        end_time = time.time()
        nuevo_bloque.tiempo_minado = round(end_time - start_time, 2)
        nuevo_bloque.recompensa = cantidad_coinbase

        coinbase_tx.aplicar_tx()

        for tx_entry in self.mempool:
            tx_obj = tx_entry["tx_obj"]
            tx_obj.aplicar_tx()

        self.agregar_bloque(nuevo_bloque)
        self.agregar_tx(coinbase_tx)
        self.recompensas.append(cantidad_coinbase)
        self.mempool.clear()
        self.fees.clear()

        print(f"Bloque {nuevo_bloque.hash} minado en {nuevo_bloque.tiempo_minado:.2f} segundos, por {minero.direccion}")

        return nuevo_bloque


    def crear_bloque_genesis(self):
        """
        Crea el bloque génesis y el usuario génesis.
        Este bloque no tiene transacciones previas y se crea con una transacción de coinbase.
        """
        # Crear el usuario génesis y la transacción de coinbase
        # El usuario génesis recibe 1000 unidades como recompensa inicial

        usuario_genesis = self.crear_usuario()
        transaccion_genesis = self.crear_coinbase_tx(minero=usuario_genesis, cantidad=1000)  

        transaccion_genesis.hacer_tx()

        bloque_genesis = Bloque(
            idx=0,
            transacciones=[transaccion_genesis.crear_dict()],
            previous_hash='0'
        )

        self.agregar_bloque(bloque_genesis)
        self.agregar_tx(transaccion_genesis)

        return usuario_genesis
    
    def crear_json(self):
        """
        Crea un diccionario con los atributos del sistema.
        """
        sistema_dict = {
            "dificultad": self.dificultad,
            "mining_reward": self.mining_reward,
            "usuarios": [usuario.crear_dict() for usuario in self.usuarios],
            "blockchain": [bloque.crear_dict() for bloque in self.blockchain],
            "UTXOs_set": [utxo.generar_dict() for utxo in self.UTXOs_set],
            "transacciones": [tx.crear_dict() for tx in self.transacciones],
            "mempool": self.mempool,
            "recompensas": self.recompensas,
            "fees": self.fees
        }
        return sistema_dict
