from django.shortcuts import get_object_or_404, redirect
from agenda.models import medioDePago
from venta.models import PagosVentas
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def pagar_deuda(request, id_pago):

    pago_select = get_object_or_404(PagosVentas, id=id_pago)
    
    if pago_select.cancelado:
        messages.error(request, 'El pago ya se encuentra cancelado.')
    else:
        pago_select.cancelado = True
        pago_select.save()

        pagos = PagosVentas.objects.filter(venta=pago_select.venta,medio_de_pago__cuenta_corriente=True)
        
        deuda=0
        for pago in pagos:
            deuda += pago.total

        pago_generado = PagosVentas.objects.create(
            venta = pago_select.venta,
            cliente = pago_select.cliente,
            medio_de_pago = medioDePago.objects.get(Nombre="Efectivo"),
            total = float(-1) * float(deuda),
        )

        messages.success(request, f'Se ha ingresado el saldo de $ {pago_generado.total} en {pago_generado.medio_de_pago.Nombre}')


    return redirect('/admin/agenda/cliente/') 

@login_required
def pagar_deuda_actualizada(request, id_pago):

    pago_select = get_object_or_404(PagosVentas, id=id_pago)
    
    if pago_select.cancelado:
        messages.error(request, 'El pago ya se encuentra cancelado.')
    else:
        pago_select.cancelado = True
        pago_select.save()


        pagos_originales = PagosVentas.objects.filter(venta=pago_select.venta,medio_de_pago__cuenta_corriente=True)
        
        deuda_original=0
        for pago in pagos_originales:
            deuda_original += pago.total


        pagos_actualizados = PagosVentas.objects.filter(venta=pago_select.venta,medio_de_pago__cuenta_corriente=True)
    
        deuda_actualizada=0
        for pago in pagos_actualizados:
       
            porcentual= float(pago.venta.pagos_en_cuenta_corriente) /  float(pago.venta.get_cart_total)
            productos = pago.venta.detalleventa_set.all()
            for producto in productos:
                deuda_actualizada += float(producto.get_total_actualizado) * float(porcentual)
        
        excedente = float(deuda_actualizada) - float(deuda_original)
        deuda = deuda_original
        
        pago_generado_1 = PagosVentas.objects.create(
            venta = pago_select.venta,
            cliente = pago_select.cliente,
            medio_de_pago = medioDePago.objects.get(Nombre="Efectivo"),
            total = float(-1) * float(deuda),
        )

        if excedente > 0:
            pago_generado_2 = PagosVentas.objects.create(
                venta = pago_select.venta,
                cliente = pago_select.cliente,
                medio_de_pago = medioDePago.objects.get(Nombre="Efectivo"),
                total = float(-1) * float(excedente),
                adicional_cc = True
            )

        if excedente > 0:
            messages.success(request, f'Se ha cancelado el saldo de $ {pago_generado_1.total:,.2f} en {pago_generado_1.medio_de_pago.Nombre} con un excedente de {excedente:,.2f} por aumento de costos.')
        else:
            messages.success(request, f'Se ha cancelado el saldo de $ {pago_generado_1.total:,.2f} en {pago_generado_1.medio_de_pago.Nombre}')

    return redirect('/admin/agenda/cliente/3/change/') 