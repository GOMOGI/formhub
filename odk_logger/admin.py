from django.contrib import admin
from odk_logger.models import XForm
from guardian.admin import GuardedModelAdmin



class FormAdmin(GuardedModelAdmin):

    list_display = ('id_string', 'user', 'form_active', 'shared')

    # A user should only see forms that belong to him.
    def queryset(self, request):
        qs = super(FormAdmin, self).queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

admin.site.register(XForm, FormAdmin)
