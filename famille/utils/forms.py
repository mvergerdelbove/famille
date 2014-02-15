from itertools import chain, izip_longest

from famille.utils import isplit, pick, repeat_lambda


class ForeignKeyForm(object):
    """
    A class used to manage foreign key addition through forms.
    """
    foreign_model = None
    origin_model_name = None
    related_name = None
    sub_form = None

    def __init__(self, *args, **kwargs):
        self.objs_to_delete, objs, instance = [], [], None

        if kwargs.get("instance", None):
            instance = kwargs["instance"]
            objs = getattr(instance, self.related_name).all()

        if kwargs.get("data", None) is not None:
            data = pick(kwargs["data"], *self.sub_form.Meta.fields)
            data = self.unzip_data(data)
            objs, self.objs_to_delete = self.compute_objs_diff(data, objs, instance)
            data = izip_longest(data, objs)
            init_forms = lambda d: self.sub_form(data=d[0], instance=d[1])
            self.sub_forms = map(init_forms, data)
        else:
            self.sub_forms = map(
                lambda o: self.sub_form(instance=o), objs
            )

        # binding an empty form anyway
        self.sub_form_empty = self.sub_form()
        super(ForeignKeyForm, self).__init__(*args, **kwargs)

    def unzip_data(self, data):
        """
        Unzip a POST data to manage several
        related object instances.
        """
        try:
            nb_objs = len(data[self.sub_form.Meta.fields[0]])
        except KeyError:
            return []

        data_list = [{} for i in xrange(nb_objs)]
        for field, values in data.iteritems():
            for i, value in enumerate(values):
                data_list[i][field] = value

        return data_list

    def compute_objs_diff(self, data, objs, instance):
        """
        Find out the right number of related objects to be saved,
        given the data and the objects that are already present.

        :param data:       list of data for sub forms
        :param objs:       objs that are already there
        :param instance:   a model instance
        """
        objs_to_delete = []
        diff = len(data) - len(objs)
        # manage obj addition
        if diff > 0:
            kwargs = {self.origin_model_name: instance}
            objs = chain(
                objs,
                repeat_lambda(lambda: self.foreign_model(**kwargs), diff)
            )
        # manage obj deletion
        elif diff < 0:
            objs, objs_to_delete = isplit(objs, len(data))

        return objs, objs_to_delete

    def is_valid(self):
        """
        Validate the form and sub forms.
        """
        is_valid = super(ForeignKeyForm, self).is_valid()
        return all((f.is_valid() for f in self.sub_forms)) and is_valid

    def save(self, *args, **kwargs):
        """
        Save the form and sub forms.
        """
        for f in self.sub_forms:
            f.save(*args, **kwargs)

        [o.delete() for o in self.objs_to_delete]
        return super(ForeignKeyForm, self).save(*args, **kwargs)