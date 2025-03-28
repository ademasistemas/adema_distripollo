from django import forms

from agenda.models import Cliente,Monedas,Configuracion
from venta.models import Venta


from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import PagosClientes, PagosVentas

class PagosClientesForm(forms.ModelForm):
    pagos_ventas = forms.ModelMultipleChoiceField(
        queryset=PagosVentas.objects.all(),
        widget=FilteredSelectMultiple("Pagos Ventas", is_stacked=False),
        required=False
    )

    class Meta:
        model = PagosClientes
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PagosClientesForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            cliente = self.instance.cliente
            self.fields['pagos_ventas'].queryset = PagosVentas.objects.filter(
                cliente=cliente,
                medio_de_pago__cuenta_corriente=True,
                cancelado=False
            )
        else:
            self.fields['pagos_ventas'].queryset = PagosVentas.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def save_m2m(self):
        self.instance.pagos_ventas.set(self.cleaned_data['pagos_ventas'])


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = {'razon_cancelacion', }
        widgets = {
            'razon_cancelacion': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
                'placeholder': 'Escriba una razón detallada'
            })
        }
        labels = {
            'razon_cancelacion': 'Razón'
        }


class VentaFacturaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), empty_label="Seleccionar cliente", widget=forms.Select(attrs={
        'class': 'form-control',
        'required': True,
    }))


    moneda = forms.ModelChoiceField(queryset=Monedas.objects.all(), empty_label="Seleccionar moneda", widget=forms.Select(attrs={
        'class': 'form-control',
        'required': False,
    }))

    class Meta:
        model = Venta
        fields = ['vendedor', 'cliente',]
    

    def save(self, commit=True):
        venta = super().save(commit=False)
        cliente = self.cleaned_data['cliente']
        vendedor = self.cleaned_data['vendedor']
        moneda = self.cleaned_data['moneda']
        venta.cliente = cliente
        venta.vendedor = vendedor
        if moneda:
            venta.facturar(cliente=cliente, vendedor=vendedor,moneda=moneda)  # Pasamos directamente los objetos cliente y vendedor.
        else:
            venta.facturar(cliente=cliente, vendedor=vendedor,moneda=Configuracion.Moneda)  # Pasamos directamente los objetos cliente y vendedor.
        if commit:
            venta.save()
        return venta