import io
import json
import pickle
import pandas as pd
import streamlit as st
from graphviz import Digraph
from src.Sistema import Sistema

st.sidebar.title("Simulación de Red Blockchain")
pags = st.sidebar.radio("Selecciona una página:", ["Inicio", "Resumen","Usuarios", "Transacciones", "Minería", "Blockchain", "Balances"])

if pags == "Inicio":
    st.title("🌐 Simulación de Red Blockchain")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Iniciar o reiniciar sistema")
        
        dificultad_inicial = st.slider("Selecciona la dificultad de minería", min_value=1, max_value=6, value=4)
        
        if st.button("Crear sistema"):
            if 'sistema' not in st.session_state:
                sistema = Sistema()
                sistema.dificultad = dificultad_inicial
                st.session_state['sistema'] = sistema
                st.session_state['sistema_creado'] = True
            
        if st.session_state.get('sistema_creado', False):
            st.success(f"Sistema creado con dificultad {st.session_state['sistema'].dificultad}.")
        
        st.subheader("Descargar sistema actual")
        if 'sistema' in st.session_state:
            buffer = io.BytesIO()
            pickle.dump(st.session_state['sistema'], buffer)
            buffer.seek(0)
            st.download_button(
                label="Descargar sistema",
                data=buffer,
                file_name='blockchain_system.pkl',
                mime='application/octet-stream'
            )
        else:
            st.warning("No hay un sistema creado para descargar.")

    with col2:
        st.subheader('Cargar sistema')  
        uploaded_file = st.file_uploader("Selecciona un archivo de sistema (.pkl)", type=["pkl"])
        if uploaded_file is not None:
            sistema_cargado = pickle.load(uploaded_file)
            st.session_state['sistema'] = sistema_cargado
            st.session_state['mensaje_exito'] = "Sistema cargado con éxito."
            st.success(st.session_state['mensaje_exito'])    
        
        st.subheader("Descargar documentación")
        if st.button("Descargar documentación"):
            with open("docs/documentacion.pdf", "rb") as f:
                st.download_button(
                    label="Descargar PDF",
                    data=f,
                    file_name="Documentación_blockchain.pdf",
                    mime="application/pdf"
                )

if pags == "Resumen":
    if 'sistema' not in st.session_state:
        st.warning("Primero debes iniciar el sistema en la página Inicio.")
    else:
        sistema = st.session_state['sistema']

    st.title("📋 Resumen del sistema")

    st.markdown("""
    <ul style='font-size:1.3em'>
        <li>Número de usuarios: <span style='color:#1f77b4'>{}</span></li>
        <li>Número de bloques: <span style='color:#1f77b4'>{}</span></li>
        <li>Número de transacciones: <span style='color:#1f77b4'>{}</span></li>
        <li>Recompensas acumuladas: <span style='color:#1f77b4'>{}</span></li>
        <li>Transacciones pendientes: <span style='color:#1f77b4'>{}</span></li>
        <li>Dificultad de minería: <span style='color:#1f77b4'>{}</span></li>
    </ul>
    """.format(
        len(sistema.usuarios),
        len(sistema.blockchain),
        len(sistema.transacciones),
        sum(sistema.recompensas),
        len(sistema.mempool),
        sistema.dificultad
    ), unsafe_allow_html=True)


elif pags == "Usuarios":
    if 'sistema' not in st.session_state:
        st.warning("Primero debes iniciar el sistema en la página Inicio.")
    else:
        sistema = st.session_state['sistema']
    st.title("👤 Usuarios")
    if st.button("Crear Usuario"):
        sistema.crear_usuario()
        st.success("Usuario creado con éxito.")
    st.subheader("Usuarios actuales:")

    df_usuarios = pd.DataFrame({
        "Usuario": [usuario.idx for usuario in sistema.usuarios],
        "Dirección": [usuario.direccion for usuario in sistema.usuarios],
        "Saldo": [usuario.checar_cartera(sistema.UTXOs_set) for usuario in sistema.usuarios]
    })
    df_usuarios.set_index("Usuario", inplace=True)

    st.write(df_usuarios)


elif pags == "Transacciones":
    if 'sistema' not in st.session_state:
        st.warning("Primero debes iniciar el sistema en la página Inicio.")
    else:
        sistema = st.session_state['sistema']

    st.title("📮 Enviar transacción")
    
    if len(sistema.usuarios) < 2:
        st.error("Se necesitan al menos dos usuarios para enviar una transacción.")
    else:
        emisores = [f'Usuario {usuario.idx}' for usuario in sistema.usuarios]
        receptores = emisores.copy()

        col1, col2 = st.columns(2)
        with col1:
            emisor_select = st.selectbox("**Remitente:**", emisores)
        with col2:
            saldo_emisor = sistema.usuarios[int(emisor_select.split()[1])].checar_cartera(sistema.UTXOs_set)
            st.container().markdown(f"**Saldo del remitente:** {saldo_emisor}")
            
        receptores = [r for r in receptores if r != emisor_select]
        receptor_select = st.selectbox("**Destinatario:**", receptores)

        cantidad = st.number_input("**Cantidad a enviar:**", min_value=0.0, value=1.0, format="%.2f")

        # comision = st.write(f"**Comisión de minería:** {sistema.mining_fee}")

        if st.button("Enviar transacción"):
            emisor = sistema.usuarios[int(emisor_select.split()[1])]
            receptor = sistema.usuarios[int(receptor_select.split()[1])]
            exito = sistema.procesar_tx(emisor, receptor, cantidad)
            if exito:
                st.success("Transacción enviada con éxito.")
            else:
                st.error("Error al enviar la transacción. Verifica los saldos y direcciones.")

elif pags == "Minería":
    if 'sistema' not in st.session_state:
        st.warning("Primero debes iniciar el sistema en la página Inicio.")
    else:
        sistema = st.session_state['sistema']

    st.title("⛏️ Minería de bloques")

    bloques_x_minar = st.markdown(
        f"\nBloque con <span style='color:red'>{len(sistema.mempool)}</span> transacciones pendientes.",
        unsafe_allow_html=True
    )
    st.write(f"Recompensa por bloque: {sistema.mining_reward}")

    if len(sistema.usuarios) == 0:
        st.error("No hay usuarios disponibles para minar.")
    else:
        mineros = [f'Usuario {usuario.idx}' for usuario in sistema.usuarios]
        minero_select = st.selectbox("Selecciona un minero:", mineros)

        if st.button("Minar bloque"):
            minero = sistema.usuarios[int(minero_select.split()[1])]
            bloque = sistema.minar_bloque(minero)

            st.success(f"Bloque {bloque.idx} minado con hash {bloque.hash}")
            st.write(f"Tiempo de minado: {bloque.tiempo_minado} s")
            st.write(f"Recompensa: {bloque.recompensa}")

elif pags == "Blockchain":
    if 'sistema' not in st.session_state:
        st.warning("Primero debes iniciar el sistema en la página Inicio.")
    else:
        sistema = st.session_state['sistema']

    st.title("Blockchain")
    
    blockchain = sistema.blockchain

    for bloque in blockchain:
        with st.expander(f"**Bloque {bloque.idx}**"):
            st.write(f"**Hash:** {bloque.hash}")
            st.write(f"**Hash anterior:** {bloque.previous_hash}")
            st.write(f"**Nonce:** {bloque.nonce}")
            st.write(f"**Timestamp:** {bloque.timestamp}")
            st.write(f"**Recompensa:** {bloque.recompensa}")
            st.write(f"**Tiempo minado:** {bloque.tiempo_minado}")

            st.write("**Transacciones:**")
            for tx in bloque.transacciones:
                st.json(tx)

    def visualizar_blockchain(blockchain):
        dot = Digraph(comment='Blockchain')
        dot.attr(rankdir='LR')

        for bloque in blockchain:
            label = f'Bloque {bloque.idx}\nNonce: {bloque.nonce}\nHash: {bloque.hash} \nTxs: {len(bloque.transacciones)}'
            dot.node(str(bloque.idx), label=label, shape='box', style='filled', color='lightblue')

        for i in range(1, len(blockchain)):
            prev_idx = blockchain[i-1].idx
            curr_idx = blockchain[i].idx
            dot.edge(str(prev_idx), str(curr_idx))
        
        return dot
    
    st.subheader("Visualización de los bloques")
    dot = visualizar_blockchain(blockchain)
    st.graphviz_chart(dot, use_container_width=True)


elif pags == "Balances":
    if 'sistema' not in st.session_state:
        st.warning("Primero debes iniciar el sistema en la página Inicio.")
    else:
        sistema = st.session_state['sistema']

    st.title("💵 Saldo de los usuarios")
    
    cartera = sistema.get_cartera()

    df_cartera = pd.DataFrame(cartera).T
    df_cartera.columns = ['Dirección', 'Saldo']
    df_cartera.index.name = 'Usuario'
    st.write(df_cartera)
