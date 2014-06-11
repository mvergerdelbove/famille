# -*- coding=utf-8 -*-
import os

from django.db.models import FileField
from django.forms import forms, MultiValueField, CharField, MultipleChoiceField, SelectMultiple
from django.template.defaultfilters import filesizeformat

from famille.utils.python import generate_timestamp
from famille.utils.widgets import RangeWidget


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

    # FIXME: use validators instead !!!!!!!
    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        if not hasattr(data.file, "content_type"):
            return data

        file = data.file
        content_type = file.content_type
        _, ext = os.path.splitext(file.name)

        if self.content_types and content_type.lower() not in self.content_types:
            raise forms.ValidationError(u'Format non supporté. Les formats valides sont: %s' % ", ".join(self.extensions))

        if self.extensions and ext.lower() not in self.extensions:
            raise forms.ValidationError(u'Format non supporté. Les formats valides sont: %s' % ", ".join(self.extensions))

        if self.max_upload_size and file._size > self.max_upload_size:
            raise forms.ValidationError('Fichier trop volumineux (max %s)' % filesizeformat(self.max_upload_size))

        return data


def upload_to_timestamp(basedir):
    """
    Generate a filename method. Useful for FileField's upload_to parameter.

    :param basedir:        the basedir in which to save the file
    """
    def wrapped(instance, filename):
        _, ext = os.path.splitext(filename)
        time_filename = "%s%s" % (generate_timestamp(), ext)
        return os.path.join(basedir, time_filename)

    return wrapped


content_type_restricted_file_field_rules = [
    ([ContentTypeRestrictedFileField, ], [],{})
]


class RangeField(MultiValueField):

    def __init__(self, field_class=CharField, min_value=None, max_value=None, widget=None, *args, **kwargs):
        self.fields = (field_class(), field_class())
        if widget:
            min_value, max_value = widget.min_value, widget.max_value

        if not 'initial' in kwargs:
            kwargs['initial'] = [min_value, max_value]

        widget = widget or RangeWidget(min_value, max_value)
        super(RangeField, self).__init__(
            fields=self.fields, widget=widget, *args, **kwargs
        )

    def compress(self, data_list):
        if data_list: # TODO
            return [
                self.fields[0].clean(data_list[0]),
                self.fields[1].clean(data_list[1])
            ]

        return None

    def clean(self, value):
        return value[1:-1] if value.startswith("[") else value


class LazyMultipleChoiceField(MultipleChoiceField):

    def _get_choices(self):
        """
        Override choices getter to cast choices to list.
        """
        return list(self._choices)

    def _set_choices(self, value):
        """
        Override choices setter to not cast directly choices to list.

        :param value:    the value to set
        """
        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)


class CommaSeparatedMultipleChoiceField(MultipleChoiceField):

    def clean(self, data):
        """
        Clean the data taken from the select. Transform
        the list of values in a coma separated string.

        :param data:      the input data
        """
        data = super(CommaSeparatedMultipleChoiceField, self).clean(data)
        return ",".join(data)


class CommaSeparatedRangeField(RangeField):

    def compress(self, data_list):
        data = super(CommaSeparatedRangeField, self).compress(data_list)
        if data:
            return ",".join(data)
        return None
