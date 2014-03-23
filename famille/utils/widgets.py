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