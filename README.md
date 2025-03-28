# Documentación del Proyecto ADEMA

## Introducción

ADEMA es un sistema desarrollado en Django que proporciona funcionalidades avanzadas para la gestión de ventas, compras, productos, reportes y múltiples configuraciones empresariales. Este documento describe la arquitectura, funcionalidades y configuraciones clave del proyecto.

---

## Tecnologías Utilizadas

- **Backend**: Django 4.x
- **Frontend**: HTML5, CSS3 (Bootstrap), JavaScript (AJAX y JQuery)
- **Base de datos**: SQLite (Desarrollo) / PostgreSQL (Producción sugerida)
- **Administración**: Jazzmin (tema para Django Admin)
- **Servidor**: Gunicorn y Nginx

---

## Estructura del Proyecto

```
adema/
├── adema/                # Configuración principal de Django
├── agenda/               # Gestión de caja, clientes y proveedores
├── producto/             # Administración de productos, precios y stock
├── venta/                # Módulo de ventas
├── compra/               # Módulo de compras
├── reportes/             # Generación de reportes mensuales y diarios
├── academia/             # Tutoriales y guías
├── pagina_web/           # Plantillas y configuración de la página pública
├── static/               # Archivos estáticos
├── templates/            # Plantillas HTML
├── db.sqlite3            # Base de datos en desarrollo
└── manage.py             # Comando principal de Django
```

---

## Funcionalidades Principales

### 1. Módulo de Productos

- **Registro de Productos**:

  - Información detallada: código, nombre, descripción, categoría y subcategoría.
  - Gestión de unidades de medida: gramos, kilos, unidades, litros, etc.
  - Manejo de stock: cálculo automático de entradas y salidas.

- **Precios**:

  - Automáticos (en base a rentabilidad configurada).
  - Manuales (opcional).

### 2. Módulo de Ventas

- **Procesos de Venta**:

  - Registro de ventas con estado: creada, pagada, facturada, finalizada o anulada.
  - Cálculo automático de costos, ganancias y totales.
  - Manejo de productos compuestos: receta de ingredientes con cantidades.

- **Pagos**:

  - Integración con múltiples métodos de pago (efectivo, cuentas corrientes).

### 3. Reportes

- **Mensuales y diarios**:
  - Ventas por producto, cliente y vendedor.
  - Gestión de caja: total inicial, ventas en efectivo, cuentas corrientes.
  - Reportes de gastos y ganancias.

### 4. Configuración

- **Empresa**:
  - Nombre, dirección, teléfono, CUIT, moneda principal y secundaria.
- **Personalización**:
  - Mostrar/ocultar fotos de productos.
  - Permitir ventas con stock negativo.

---

## Configuración de Entorno

### Variables de Entorno

- **SECRET\_KEY**: Clave secreta de Django.
- **DEBUG**: `True` (Desarrollo) / `False` (Producción).
- **ALLOWED\_HOSTS**: Lista de dominios permitidos.

### Configuración de Archivos Estáticos y Media

- Desarrollo:
  ```
  STATIC_URL = '/static/'
  STATIC_ROOT = os.path.join(BASE_DIR, 'static')
  MEDIA_URL = '/media/'
  MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
  ```
- Producción:
  ```
  STATIC_ROOT = '/ruta/produccion/static/'
  MEDIA_ROOT = '/ruta/produccion/media/'
  ```

---

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone <url-del-repositorio>
   cd adema
   ```

2. Crear un entorno virtual:

   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configurar las variables de entorno.

5. Realizar migraciones:

   ```bash
   python manage.py migrate
   ```

6. Crear un superusuario:

   ```bash
   python manage.py createsuperuser
   ```

7. Iniciar el servidor:

   ```bash
   python manage.py runserver
   ```

---

## Próximos Pasos

1. **Pruebas**:
   - Implementar `pytest` para pruebas automatizadas.
2. **Seguridad**:
   - Almacenar la `SECRET_KEY` y configuraciones sensibles en un archivo `.env`.
3. **Despliegue**:
   - Configurar Nginx y Gunicorn para producción.

---

## Contacto

**Desarrollador**: Kevin Turquiñich\
**Correo**: [soporte@pantutienda.com](mailto\:soporte@pantutienda.com)

esto iria en un readme.md no?

