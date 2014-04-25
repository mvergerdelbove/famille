from django.contrib.flatpages.admin import FlatpageForm
from django.contrib.flatpages.models import FlatPage
from tinymce.widgets import TinyMCE


class TinyMCEForm(FlatpageForm):
    class Meta:
        model = FlatPage
        widgets = {
            'content': TinyMCE(attrs={'cols': 100, 'rows': 30}, content_language="fr")
        }
