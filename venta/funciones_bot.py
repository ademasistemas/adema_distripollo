# funciones_bot.py
from .funciones_extraccion import extraer_producto
from agenda.models import Cliente,Proveedor

def consultar_precio(texto, estado=None):
    productos = extraer_producto(texto=texto)

    if productos.count() == 0:
        # No se encontró ningún producto
        return f"No se encontró ningún producto con el código o descripción '{texto}'. ¿Deseas intentar nuevamente?"

    elif productos.count() == 1:
        # Se encontró un solo producto, mostrar detalles directamente
        producto = productos.first()
        precio = producto.precio_venta()
        stock = producto.stock_actual_str()
        return f"Producto encontrado: {producto.nombre}. Precio: ${precio}. Stock disponible: {stock}."

    else:
        # Verifica si 'estado' es None y crea un diccionario vacío si es necesario
        if estado is None:
            estado = {}

        # Se encontraron varios productos, mostrar una lista y permitir seleccionar
        opciones = "\n".join([f"{i+1}. {producto.nombre} (Código: {producto.codigo})" for i, producto in enumerate(productos)])
        estado['productos_encontrados'] = productos  # Guardar los productos encontrados en el estado del usuario
        return f"Se encontraron varios productos. Por favor, selecciona uno de la lista:\n{opciones}\nEscribe el número o código del producto que deseas seleccionar."

def seleccionar_producto(pregunta, estado):
    # Si el usuario ya tiene una lista de productos encontrados, permitir seleccionar uno
    productos = estado.get('productos_encontrados')
    if productos:
        if pregunta.isdigit() and int(pregunta) <= productos.count():
            # Si el usuario selecciona un número de la lista
            producto_seleccionado = productos[int(pregunta) - 1]
        else:
            # Si el usuario introduce un código de producto
            producto_seleccionado = productos.filter(codigo=pregunta).first()

        if producto_seleccionado:
            precio = producto_seleccionado.precio_venta()
            stock = producto_seleccionado.stock_actual_str()
            return f"Producto seleccionado: {producto_seleccionado.nombre}. Precio: ${precio}. Stock disponible: {stock}."
        else:
            return f"El producto seleccionado no es válido. Por favor, selecciona un número o código correcto."
    return "No hay productos para seleccionar."

def consultar_agenda_proveedor(texto):
    proveedor = Proveedor.objects.filter(id=texto).first() if texto.isdigit() else Proveedor.objects.filter(Empresa__icontains=texto).first()

    if proveedor:
        return f"Proveedor encontrado: {proveedor.Empresa}."
    else:
        return f"No se encontró ningún proveedor con el nombre o número '{texto}'."

def consultar_agenda_cliente(texto):
    # Buscar cliente por número o nombre
    cliente = Cliente.objects.filter(codigo=texto).first() or Cliente.objects.filter(codigo=texto).first() if texto.isdigit() else Cliente.objects.filter(nombre__icontains=texto).first()

    if cliente:
        return f"Encontre el siguiente cliente: {cliente}."
    else:
        return f"No se encontró ningún cliente con este parámetro '{texto}'."


def consultar_cuenta_corriente_cliente(texto):
    proveedor = Proveedor.objects.filter(numero=texto).first() if texto.isdigit() else Proveedor.objects.filter(Empresa__icontains=texto).first()

    # Verificar si el texto es un número de cliente o un nombre
    if texto.isdigit():
        # Buscar cliente por número
        return f"Buscando Cuenta Corriente cliente con número {texto}..."
    else:
        # Buscar cliente por nombre o apellido
        return f"Buscando Cuenta Corriente del cliente con nombre '{texto}'..."

def consultar_cuenta_corriente_proveedor(texto):
    cliente = Cliente.objects.filter(codigo=texto).first() if texto.isdigit() else Cliente.objects.filter(nombre__icontains=texto).first()

    # Verificar si el texto es un número de proveedor, nombre o empresa
    if cliente:
        return f'Encontre a {cliente}'
    else:
        return 'No he encontrado ningun cliente.'