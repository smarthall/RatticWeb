from django.db.models import FileField, CharField
from django.core import validators
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules


# Allow South to inspect our fields
add_introspection_rules([], [
    "^cred\.fields\.SizedFileField",
    "^cred\.fields\.URIField",
])


class SizedFileField(FileField):
    def __init__(self, *args, **kwargs):
        # Get the upload size we were given
        self.max_upload_size = kwargs.pop('max_upload_size', None)

        super(SizedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(SizedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            # If the file is bigger than we expected, give an error
            if file._size > self.max_upload_size:
                raise forms.ValidationError(_('File size must be under %s. Current file size is %s.') % (filesizeformat(self.max_upload_size), filesizeformat(data.size)))
        except AttributeError:
            pass

        return data


class URIField(CharField):
    default_validators = [validators.URLValidator()]
    description = _("URI")

    def __init__(self, verbose_name=None, name=None, **kwargs):
        kwargs['max_length'] = kwargs.get('max_length', 200)
        super(URIField, self).__init__(verbose_name, name, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(URIField, self).deconstruct()
        if kwargs.get("max_length", None) == 200:
            del kwargs['max_length']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # As with CharField, this will cause URL validation to be performed
        # twice.
        defaults = {
            'form_class': forms.URLField,
        }
        defaults.update(kwargs)
        return super(URIField, self).formfield(**defaults)
