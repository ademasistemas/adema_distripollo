from django.http import Http404
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView, DeleteView, CreateView
from agenda.models import Configuracion
from django.core.paginator import Paginator
from producto.forms import ProductoForm, CategoriaForm
from producto.models import Producto, Categoria
import pandas as pd
from django.http import HttpResponse

class ProductManage(ListView):
    model = Producto
    template_name_suffix = '_manage'
    context_object_name = "producto_list"
    paginate_by = 20  # Número de productos por página

    def get_queryset(self):
        queryset = Producto.objects.exclude(habilitar_venta=False).filter(productoprecio__isnull=False).distinct()
        configuracion = Configuracion.objects.first()

        if configuracion and configuracion.stock_negativo_ldp:
            queryset = queryset.exclude(id__in=[p.id for p in queryset if p.stock_es_negativo])

        # Orden por defecto 'codigo'
        orden = self.request.GET.get('orden', 'codigo')
        sentido = self.request.GET.get('sentido', 'asc')

        # Validar campos de ordenación
        campos_validos = ['codigo', 'nombre', 'categoria__nombre']
        if orden in campos_validos:
            orden_campo = orden if sentido == 'asc' else f'-{orden}'
            queryset = queryset.order_by(orden_campo)

        return queryset  # No paginamos aquí, solo ordenamos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        configuracion = Configuracion.objects.first()
        queryset = self.get_queryset()

        try:
            context['decimales'] = int(configuracion.mostrar_decimales)
        except (ValueError, TypeError, AttributeError):
            context['decimales'] = 2
        context['configuracion'] = configuracion


        # Paginación manual con Paginator
        paginator = Paginator(queryset, self.paginate_by)  # Dividir el queryset en páginas
        page_number = self.request.GET.get('page', 1)  # Obtener el número de página desde la URL
        page_obj = paginator.get_page(page_number)  # Obtener la página actual

        context['producto_list'] = page_obj.object_list  # Productos de la página actual
        context['page_obj'] = page_obj  # Página actual para la paginación
        context['paginator'] = paginator  # Para acceder a la cantidad total de páginas

        # Datos adicionales
        context['orden'] = self.request.GET.get('orden', 'codigo')
        context['sentido'] = self.request.GET.get('sentido', 'asc')
        context['configuracion'] = configuracion

        return context


def descargar_productos_gestionar(request):
    """
    Genera y descarga un archivo Excel con la lista completa de productos en 'gestionar'.
    - Se incluyen descripciones y unidades de cada precio.
    - Se agregan columnas "Solicitado" y "Total" como plantilla para pedidos.
    """
    productos = Producto.objects.filter(habilitar_venta=True).order_by('nombre')

    # Determinar el número máximo de precios por producto
    max_precios = max([producto.productos_precio.count() for producto in productos] + [1])  # Al menos una columna

    # Crear la estructura de datos para el DataFrame
    data = []
    for producto in productos:
        precios = producto.productos_precio.all()[:max_precios]  # Obtener los precios del producto
        precios_columnas = []
        descripciones_columnas = []
        unidades_columnas = []

        # Extraer información de precios
        for precio in precios:
            precios_columnas.append(precio.precio())
            descripciones_columnas.append(f'x {precio.cantidad} {precio.unidad_de_medida}')
            unidades_columnas.append(precio.unidad_de_medida)

        # Rellenar con None si hay menos precios que el máximo
        while len(precios_columnas) < max_precios:
            precios_columnas.append(None)
            descripciones_columnas.append(None)
            unidades_columnas.append(None)

        # Aplanar listas correctamente (antes usábamos `sum()` que generaba error)
        precio_data = []
        for desc, price, unit in zip(descripciones_columnas, precios_columnas, unidades_columnas):
            precio_data.extend([desc, price, unit])  # Agregar elementos uno por uno

        # Agregar fila con columnas dinámicas
        data.append([
            producto.id,
            producto.codigo if producto.codigo else "N/A",
            producto.nombre,
            producto.descripcion if producto.descripcion else "Sin descripción",
            producto.categoria.nombre if producto.categoria else "Sin categoría",
            producto.stock_actual(),
            None,  # Columna "Solicitado" vacía para ingresar manualmente
            None   # Columna "Total" que se llenará con la fórmula en Excel
        ] + precio_data)  # Concatenar correctamente los datos

    # Crear nombres de columnas dinámicamente
    precio_columnas = [f'Precio_{i+1}' for i in range(max_precios)]
    descripcion_columnas = [f'Descripcion_{i+1}' for i in range(max_precios)]
    unidad_columnas = [f'Unidad_{i+1}' for i in range(max_precios)]
    
    # Alternar las columnas de descripción, precio y unidad
    columnas = ['ID', 'Código', 'Nombre', 'Descripción', 'Categoría', 'Stock', 'Solicitado', 'Total']
    for i in range(max_precios):
        columnas.append(descripcion_columnas[i])
        columnas.append(precio_columnas[i])
        columnas.append(unidad_columnas[i])

    # Crear DataFrame con Pandas
    df = pd.DataFrame(data, columns=columnas)

    # Crear respuesta HTTP con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="productos_pedido.xlsx"'

    with pd.ExcelWriter(response, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Productos")

        # Cargar el workbook y agregar fórmula en la columna "Total"
        workbook = writer.book
        worksheet = writer.sheets["Productos"]
        
        for row in range(2, len(df) + 2):  # Desde la segunda fila
            worksheet[f'H{row}'] = f"=G{row}*J{row}"  # Multiplica 'Solicitado' x 'Precio_1'

    return response




class ProductCreate(CreateView):
    model = Producto
    form_class = ProductoForm
    success_url = reverse_lazy('producto:manage')


class ProductUpdate(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name_suffix = '_update_form'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductUpdate, self).get_context_data(**kwargs)
        producto = Producto.objects.get(id=self.kwargs['pk'])
        
        if not producto:
            raise Http404
        else:
            # Añadimos al contexto el objeto del producto
            context['nombre'] = producto.nombre
            
        return context

    def get_success_url(self):
        return reverse_lazy('producto:manage')

class ProductoDelete(DeleteView):
    model = Producto
    success_url = reverse_lazy('producto:manage')


class CategoriaList(ListView):
    model = Categoria


class CategoriaCreate(CreateView):
    model = Categoria
    form_class = CategoriaForm
    success_url = reverse_lazy('producto:categoria_index')


class CategoriaUpdate(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name_suffix = '_update_form'

    def get_success_url(self):
        return reverse_lazy('producto:categoria_index')


class CategoriaDelete(DeleteView):
    model = Categoria
    success_url = reverse_lazy('producto:categoria_index')
