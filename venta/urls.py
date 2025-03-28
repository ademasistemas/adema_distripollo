from django.urls import path
from . import views, ticket_dispatcher


venta_patterns = ([ 
                    path('', views.product_list, name='product_list'),
                    path('carta/', views.carta_01_qr, name='carta_qr'),
                    path('ventas/', views.VentaList.as_view(), name='ventas'),
                    #path('compras/', views.compra, name='compra'), 
                    path('reporte_ventas/', views.reporte_ventas, name='reporte_ventas'),   
                    path('reporte_ganancias/', views.reporte_ganancias, name='reporte_ganancias'),
                    path('ventasPorProducto/', views.dashboard, name='ventasPorProducto'),
                    path('ventas/detail/<int:pk>/', views.VentaDetail.as_view(), name='detail'),
                    path('ventas/anular/<int:pk>/', views.VentaUpdate.as_view(), name='anular'),
                    path('ventas/facturar/<int:pk>/', views.VentaFactura.as_view(), name='facturar'),
                    path('imprimir/<int:venta_id>/', views.imprimir_ticket, name='imprimir'),
                    #path('imprimir_ticket/<int:venta_id>/', views.PrintTicketPDFView.as_view(), name='imprimir_ticket'),
                    # path('imprimir_ticket/<int:venta_id>/', view_ticket_comandera.ImprimirTicketCommanderaView.as_view(), name='imprimir_ticket'),
                    path('imprimir_ticket/<int:venta_id>/', ticket_dispatcher.imprimir_ticket, name='imprimir_ticket'),
                    path('carrito/', views.carrito, name='carrito'),
                    path('entregar/<int:venta_id>/', views.entregar_venta, name='entregar_venta'),
                    path('generar_ticket/<int:pago_id>/', views.generar_ticket, name='generar_ticket'),

                ], 'venta')

