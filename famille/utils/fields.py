# -*- coding=utf-8 -*-
import os

from django.db.models import FileField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        - content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        - max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB   - 5242880
            10MB  - 10485760
            20MB  - 20971520
            50MB  - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", None)
        self.max_upload_size = kwargs.pop("max_upload_size", None)
        self.extensions = kwargs.pop("extensions", None)

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        content_type = file.content_type
        _, ext = os.path.splitext(file.name)

        if self.content_types and content_type not in self.content_types:
            raise forms.ValidationError(u'Format non supporté')

        if self.extensions and ext not in self.extensions:
            raise forms.ValidationError(u'Format non supporté')

        if self.max_upload_size and file._size > self.max_upload_size:
            raise forms.ValidationError('Fichier trop volumineux (max %s)' % filesizeformat(self.max_upload_size))

        return data

content_type_restricted_file_field_rules = [
    ([ContentTypeRestrictedFileField, ], [],{})
]