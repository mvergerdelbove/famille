# -*- coding=utf-8 -*-
from django.forms import widgets
from django.forms.util import flatatt
from django.utils.html import format_html


class RatingWidget(widgets.HiddenInput):

    total = 5

    def __init__(self, attrs=None):
        if attrs is not None:
            self.total = attrs.pop('total', self.total)
            star_class = attrs.pop("star_class", "")
            self.star_attrs = attrs.copy()
            self.star_attrs["class"] = star_class

        super(RatingWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        value = int(value)
        remaining = min(self.total - value, self.total)

        html = (value * self.render_star()) + (remaining * self.render_star(empty=True))
        return html + super(RatingWidget, self).render(name, value, attrs)

    def render_star(self, empty=False):
        html_class = " glyphicon glyphicon-star-empty" if empty else " glyphicon glyphicon-star"
        attrs = self.star_attrs.copy()
        attrs["class"] += html_class
        return format_html('<i {0}></i>', flatatt(attrs))


class RangeWidget(widgets.TextInput):

    def __init__(self, min_value, max_value, attrs=None):
        super(RangeWidget, self).__init__(attrs)
        self.min_value = min_value
        self.max_value = max_value

    def decompress(self, value):
        return value

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        value = value or [self.min_value, self.max_value]
        value = [int(v) for v in value.split(",")] if isinstance(value, basestring) else value

        attrs["data-slider-value"] = str(value)
        attrs["data-slider-min"] = self.min_value
        attrs["data-slider-max"]= self.max_value
        attrs["data-slider-tooltip-template"]= u"de {0} à {1} €"

        return super(RangeWidget, self).render(name, value, attrs)


class CommaSeparatedMultipleChoiceWidget(widgets.SelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        """
        Override render to cast value to list.
        """
        value = value or ""
        value = value.split(",")
        return super(CommaSeparatedMultipleChoiceWidget, self).render(name, value, attrs, choices)
