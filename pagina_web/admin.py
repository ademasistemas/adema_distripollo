from django.contrib import admin
from django.db import models
from django.forms import TextInput
from .models import LandingPage

@admin.register(LandingPage)
class LandingPageAdmin(admin.ModelAdmin):
    list_display = ("activa","nombre","title")
    list_display_links = ("activa","nombre","title")
    fieldsets = (
        ("Encabezado", {
            "fields": ("nombre","activa","logo", "title", "telefono", "hero_title", "hero_description", "hero_image")
        }),
        ("Sobre Nosotros", {
            "fields": ("about_title","about_logo", "about_text1", "about_text2", "about_image", "about_color", "about_font_color")
        }),
        ("Platos Destacados", {
            "fields": (
                "especialidades_title",'especialidades_bg_color','especialidades_font_color',
                ("especialidades_dish1_title", "especialidades_dish1_description", "especialidades_dish1_image"),
                ("especialidades_dish2_title", "especialidades_dish2_description", "especialidades_dish2_image"),
                ("especialidades_dish3_title", "especialidades_dish3_description", "especialidades_dish3_image"),
                ("especialidades_dish4_title", "especialidades_dish4_description", "especialidades_dish4_image"),
            )
        }),

        ("Testimonios", {
            "fields": (
                "testimonials_title", 
                "testimonials_bg_color", 
                "testimonials_font_color",
                ("testimonial1", "testimonial1_author", "testimonial1_logo"),
                ("testimonial2", "testimonial2_author", "testimonial2_logo"),
                ("testimonial3", "testimonial3_author", "testimonial3_logo"),
            )
        }),

        ("Ubicación", {
            "fields": (
                "location_title", "address", "schedule",
            )
        }),
        ("Contacto", {
            "fields": (
                "contact_title", "contact_phone", "contact_email",
            )
        }),

    )

    # Define los widgets para los selectores de color
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ['about_color', 
                            'about_font_color',
                            'especialidades_bg_color',
                            'especialidades_font_color',
                            'testimonials_bg_color',
                            ]:
            kwargs['widget'] = TextInput(attrs={'type': 'color'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)
