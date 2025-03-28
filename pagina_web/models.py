# pagina_web/models.py

from django.db import models

class LandingPage(models.Model):


    nombre = models.CharField(max_length=255, default="Página de Inicio")


    # Seccion Encabezado ---------> 
    logo = models.ImageField(blank=True, null=True)
    title = models.CharField(max_length=255, default="Excel-ente")
    telefono = models.CharField(max_length=255, default="541112345678")
    hero_title = models.CharField(max_length=255, default="Bienvenidos a Delicious Bites")
    hero_description = models.TextField(default="Experiencia culinaria excepcional en cada bocado")
    hero_image = models.ImageField(upload_to='landing/', blank=True, null=True)
    
    activa = models.BooleanField(default=False)


    # Seccion Sobre Nosotros ---------> 
    about_logo = models.ImageField(blank=True, null=True)
    about_title = models.CharField(max_length=255, default="Sobre Nosotros")
    about_text1 = models.TextField(default="Texto 1 sobre nosotros")
    about_text2 = models.TextField(default="Texto 2 sobre nosotros")
    about_image = models.ImageField(upload_to='landing/', blank=True, null=True)
    about_color = models.CharField(
        max_length=7, 
        default="#f0f0f0",  # Valor hexadecimal por defecto
        help_text="Color de fondo en formato hexadecimal (ejemplo: #f0f0f0)"
    )
    about_font_color = models.CharField(
        max_length=7, 
        default="#000000",  # Negro por defecto
        help_text="Color del texto en formato hexadecimal (ejemplo: #000000)"
    )

    # Seccion  Platos destacados  ---------> 
    especialidades_title = models.CharField(max_length=255, default="Platos Destacados")
    especialidades_dish1_title = models.CharField(max_length=100, default="Plato 1")
    especialidades_dish1_description = models.TextField(default="Descripción Plato 1")
    especialidades_dish1_image = models.ImageField(upload_to='landing/', blank=True, null=True)
    especialidades_dish2_title = models.CharField(max_length=100, default="Plato 2")
    especialidades_dish2_description = models.TextField(default="Descripción Plato 2")
    especialidades_dish2_image = models.ImageField(upload_to='landing/', blank=True, null=True)
    especialidades_dish3_title = models.CharField(max_length=100, default="Plato 3")
    especialidades_dish3_description = models.TextField(default="Descripción Plato 3")
    especialidades_dish3_image = models.ImageField(upload_to='landing/', blank=True, null=True)
    especialidades_dish4_title = models.CharField(max_length=100, default="Plato 3")
    especialidades_dish4_description = models.TextField(default="Descripción Plato 3")
    especialidades_dish4_image = models.ImageField(upload_to='landing/', blank=True, null=True)
    especialidades_bg_color = models.CharField(
        max_length=7, 
        default="#f0f0f0",  # Valor hexadecimal por defecto
        help_text="Color de fondo en formato hexadecimal (ejemplo: #f0f0f0)"
    )
    especialidades_font_color = models.CharField(
        max_length=7, 
        default="#000000",  # Negro por defecto
        help_text="Color del texto en formato hexadecimal (ejemplo: #000000)"
    )



    # Seccion Testimonios  ---------> 
    testimonials_title = models.CharField(max_length=255, default="Lo que dicen nuestros clientes")
    
    testimonial1 = models.TextField(default="Testimonio 1")
    testimonial1_author = models.CharField(max_length=100, default="Autor Testimonio 1")
    testimonial1_logo = models.ImageField(upload_to='landing/', blank=True, null=True)

    testimonial2 = models.TextField(default="Testimonio 2")
    testimonial2_author = models.CharField(max_length=100, default="Autor Testimonio 2")
    testimonial2_logo = models.ImageField(upload_to='landing/', blank=True, null=True)

    testimonial3 = models.TextField(default="Testimonio 3")
    testimonial3_author = models.CharField(max_length=100, default="Autor Testimonio 3")
    testimonial3_logo = models.ImageField(upload_to='landing/', blank=True, null=True)

    testimonials_bg_color = models.CharField(
        max_length=7, 
        default="#f0f0f0",  
        help_text="Color de fondo en formato hexadecimal (ejemplo: #f0f0f0)"
    )
    testimonials_font_color = models.CharField(
        max_length=7, 
        default="#000000",  
        help_text="Color del texto en formato hexadecimal (ejemplo: #000000)"
    )

    # Ubicación  ---------> 
    location_title = models.CharField(max_length=255, default="Nuestra Ubicación")
    address = models.TextField(default="Calle Principal, 123\n[Tu Ciudad], [Código Postal]")
    schedule = models.TextField(default="Lunes a Viernes: 12:00 - 22:00\nSábado y Domingo: 12:00 - 23:00")

    # Contacto  ---------> 
    contact_title = models.CharField(max_length=255, default="Contacto")
    contact_phone = models.CharField(max_length=20, default="(123) 456-7890")
    contact_email = models.EmailField(default="contacto@deliciousbites.com")


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Landing'
        verbose_name_plural = 'Pagina web' 

    def get_about_background(self):
        if self.about_image and self.about_image.url:
            return f"url('{self.about_image.url}')"
        return self.about_color 