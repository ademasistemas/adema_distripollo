from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from .models import PagosProveedores, medioDePagoCompra

class PagosProveedoresForm(forms.ModelForm):
    pagos_pendientes = forms.ModelMultipleChoiceField(
        queryset=medioDePagoCompra.objects.filter(cancelado=False),
        widget=FilteredSelectMultiple("Pagos Pendientes", is_stacked=False),
        required=False
    )

    class Meta:
        model = PagosProveedores
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PagosProveedoresForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['pagos_pendientes'].queryset = medioDePagoCompra.objects.filter(
                Compra__proveedor=self.instance.proveedor,
                cancelado=False
            )
        else:
            self.fields['pagos_pendientes'].queryset = medioDePagoCompra.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance

    def save_m2m(self):
        self.instance.pagos_pendientes.set(self.cleaned_data['pagos_pendientes'])
