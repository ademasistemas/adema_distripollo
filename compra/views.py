from compra.models import Compra, PagosProveedores
from .forms import PagosProveedoresForm
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect,render
from agenda.models import Configuracion, medioDeCompra
from compra.models import medioDePagoCompra
from producto.models import Producto
from django.contrib.auth.decorators import login_required

@login_required
def pagar_deuda_proveedores(request, id_pago):
    pago_select = get_object_or_404(medioDePagoCompra, id=id_pago)

    if request.method == 'POST':
        form = PagosProveedoresForm(request.POST)
        if form.is_valid():
            pago_proveedores = form.save(commit=False)
            pagos_pendientes = form.cleaned_data['pagos_pendientes']
            total_pendiente = sum(pago.Total for pago in pagos_pendientes)

            if pago_proveedores.total < total_pendiente:
                messages.error(request, "El total pagado no cubre el total de los pagos seleccionados.")
            else:
                pago_proveedores.save()
                form.save_m2m()
                for pago in pagos_pendientes:
                    pago.cancelado = True
                    pago.save()
                messages.success(request, "Pago registrado correctamente.")
                return redirect('admin:compra_pagosproveedores_changelist')
    else:
        form = PagosProveedoresForm()
    
    context = {
        'title': 'Pagar Deuda Proveedores',
        'opts': PagosProveedores._meta,
        'form': form,
    }
    return render(request, 'admin/compra/pagar_deuda_proveedores.html', context)

@login_required
def compras_list(request):


    compra_list = Compra.objects.all()

    
    context = {'compra_list': compra_list}

    return render(request, 'compra/compra_list.html', context)

@login_required
def pagar_deuda_proveedor(request, id_pago):

    pago_select = get_object_or_404(medioDePagoCompra, id=id_pago)

    pago_select.cancelado = True
    pago_select.save()


    #pagos = medioDePagoCompra.objects.filter(Compra=pago_select.Compra,Cuenta__cuenta_corriente=True)
    deuda=pago_select.Total #0
    # for pago in pagos:
    #     deuda += pago.Total

    pago_generado = medioDePagoCompra.objects.create(
        Compra = pago_select.Compra,
        Cuenta = medioDeCompra.objects.get(Nombre="Efectivo"),
        Total = float(-1) * float(deuda),
        cancelado = True,
    )

    messages.success(request, f'Se ha cancelado el saldo con el proveedor {pago_generado.Compra.proveedor} por $ {pago_generado.Total:,.2f} .')


    return redirect('/admin/compra/mediodepagocompra/') 