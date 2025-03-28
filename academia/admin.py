from django.contrib import admin
from .models import Tutorial,TutorialCategory
from import_export.admin import ImportExportModelAdmin

@admin.register(Tutorial)
class TutorialAdmin(ImportExportModelAdmin):
    list_display = ('title','category',)



@admin.register(TutorialCategory)
class TutorialAdmin(ImportExportModelAdmin):
    list_display = ('name','slug',)

