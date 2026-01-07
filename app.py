import streamlit as st
from db import (
    create_tables,
    eliminar_pedido,
    eliminar_detalle_pedido,
    actualizar_total_pedido,
    obtener_productos,
    obtener_pedidos,
    cargar_productos_iniciales,
    obtener_o_crear_cliente,
    crear_pedido,
    agregar_detalle_pedido,
    obtener_detalle_pedido
)

# -------------------------
# CONFIGURACIÓN
# -------------------------
st.set_page_config(
    page_title="Pupusería Los Gemelos",
    layout="wide"
)

create_tables()
st.title(" Pupusería Los Gemelos ")

# -------------------------
# ESTILOS
# -------------------------
st.markdown("""
<style>
.card {
    padding: 15px;
    border-radius: 10px;
    background-color: #f9f9f9;
    margin-bottom: 10px;
    border: 1px solid #ddd;
}
.price {
    font-weight: bold;
    color: #2e7d32;
}
.total {
    font-size: 24px;
    font-weight: bold;
    color: #1b5e20;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# ESTADO
# -------------------------
if "ticket" not in st.session_state:
    st.session_state.ticket = {}

if "pedido_en_edicion" not in st.session_state:
    st.session_state.pedido_en_edicion = None

# -------------------------
# FUNCIONES
# -------------------------
def agregar_producto(nombre, cantidad, precio):
    if nombre in st.session_state.ticket:
        st.session_state.ticket[nombre]["cantidad"] += cantidad
    else:
        st.session_state.ticket[nombre] = {
            "precio": precio,
            "cantidad": cantidad
        }

def quitar_producto(nombre):
    st.session_state.ticket.pop(nombre, None)

def calcular_total():
    return sum(
        p["precio"] * p["cantidad"]
        for p in st.session_state.ticket.values()
    )

def disminuir_producto(nombre):
    if nombre in st.session_state.ticket:
        if st.session_state.ticket[nombre]["cantidad"] > 1:
            st.session_state.ticket[nombre]["cantidad"] -= 1
        else:
            del st.session_state.ticket[nombre]

def resetear_cantidades():
    for key in list(st.session_state.keys()):
        if key.startswith("qty_"):
            del st.session_state[key]




# -------------------------
# CARGAR PRODUCTOS
# -------------------------
if st.button(" Cargar productos iniciales "):
    cargar_productos_iniciales()
    st.success("Productos cargados")

productos = {
    nombre: {"id": pid, "precio": precio}
    for pid, nombre, precio in obtener_productos()
}
categorias = {
    " PUPUSAS ": ["Pupusa Revuelta", "Pupusa de Queso",],
    " SODAS ": ["Soda Coca Cola", "Soda Fanta", "Soda Tropical Uva"],
    " BEBIDAS CALIENTES ": ["Café", "Chocolate"],
    " JUGOS": ["Jugo valle Mandarina", "Jugo de Naranja" ],
    " AGUA ": ["Botella Agua Cristal 600ml"]
}


# -------------------------
# INTERFAZ
# -------------------------
col1, col2 = st.columns([2, 1])

# ========= PRODUCTOS =========
with col1:
    st.subheader(" PRODUCTOS ")

    for categoria, lista_productos in categorias.items():

        with st.expander(categoria, expanded=True):

            for nombre in lista_productos:

                if nombre not in productos:
                    continue

                datos = productos[nombre]

                c1, c2, c3, c4 = st.columns([3, 1.2, 1.2, 1.5])

                with c1:
                    st.write(nombre)

                with c2:
                    st.write(f"${datos['precio']:.2f}")

                with c3:
                    cantidad = st.number_input(
                        "Cant.",
                        min_value=1,
                        step=1,
                        key=f"qty_{nombre}"
                    )

                with c4:
                    if st.button("AGREGAR", key=f"add_{nombre}"):
                        agregar_producto(nombre, cantidad, datos["precio"])
                        st.rerun()


# ========= PEDIDO =========
with col2:
    st.subheader(" PEDIDO ACTUAL ")

    nombre_cliente = st.text_input(
        "Nombre del cliente",
        value=st.session_state.get("nombre_cliente", "")
    )

    if not st.session_state.ticket:
        st.info("No hay productos agregados")

    else:
        for nombre, datos in st.session_state.ticket.items():
            subtotal = datos["precio"] * datos["cantidad"]

            col_a, col_b, col_c = st.columns([6, 1, 1])

            with col_a:
                st.write(f"{datos['cantidad']} x {nombre} — ${subtotal:.2f}")

            with col_b:
                if st.button(" ➖ ", key=f"minus_{nombre}"):
                    disminuir_producto(nombre)
                    st.rerun()

            with col_c:
                if st.button(" ❌ ", key=f"delete_{nombre}"):
                    quitar_producto(nombre)
                    st.rerun()

        total = calcular_total()
        st.success(f"Total a pagar: ${total:.2f}")

    # -------- GUARDAR PEDIDO --------
    if st.button(" GUARDAR ", use_container_width=True):

        if not nombre_cliente.strip():
            st.error("Ingrese el nombre del cliente")

        elif not st.session_state.ticket:
            st.error("El pedido está vacío")

        else:
            total = calcular_total()

            #  EDITAR PEDIDO
            if st.session_state.pedido_en_edicion:
                pid = st.session_state.pedido_en_edicion
                eliminar_detalle_pedido(pid)
                actualizar_total_pedido(pid, total)

            #  NUEVO PEDIDO
            else:
                cliente_id = obtener_o_crear_cliente(nombre_cliente)
                pid = crear_pedido(cliente_id, total)

            for nombre, datos in st.session_state.ticket.items():
                agregar_detalle_pedido(
                    pid,
                    productos[nombre]["id"],
                    datos["cantidad"],
                    datos["precio"]
                )

            st.success("Pedido guardado correctamente")

            # LIMPIARTODO
            st.session_state.ticket = {}
            st.session_state.pedido_en_edicion = None
            st.session_state.nombre_cliente = ""

            resetear_cantidades()

            st.rerun()



# ===============================
# PEDIDOS GUARDADOS
# ===============================
st.divider()
st.subheader(" LISTA DE PEDIDOS ")

pedidos = obtener_pedidos()

if not pedidos:
    st.info("No hay pedidos pendientes")
else:
    for pid, cliente, total in pedidos:

        with st.expander(f"{cliente}  |  Total: ${total:.2f}"):

            detalle = obtener_detalle_pedido(pid)

            if detalle:
                for nombre, cantidad, precio, subtotal in detalle:
                    st.write(f"- {cantidad} x {nombre} → ${subtotal:.2f}")
            else:
                st.write("Pedido sin productos")

            st.markdown(f"** Total a pagar: ${total:.2f}**")
            st.divider()

            col1, col2 = st.columns(2)

            #  EDITAR PEDIDO
            with col1:
                if st.button(" Editar", key=f"edit_{pid}"):
                    st.session_state.pedido_en_edicion = pid
                    st.session_state.ticket = {}

                    # Recuperar nombre del cliente
                    st.session_state.nombre_cliente = cliente

                    for nombre, cantidad, precio, _ in detalle:
                        st.session_state.ticket[nombre] = {
                            "precio": precio,
                            "cantidad": cantidad
                        }

                    st.rerun()

            #  ELIMINAR PEDIDO
            with col2:
                if st.button(" Eliminar ", key=f"delete_{pid}"):
                    eliminar_pedido(pid)
                    st.success("Pedido eliminado")
                    st.rerun()


