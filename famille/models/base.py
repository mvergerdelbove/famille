from django.db import models


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    class Meta:
        abstract = True

    @property
    def simple_id(self):
        """
        A simple id for any model (simple way of serialization),
        in order to avoid too many foreign key relationships when
        too complicated.
        """
        return "%s__%s" % (self.__class__.__name__.lower(), self.pk)
