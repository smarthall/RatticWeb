from django.db.models import FileField, TextField, SubfieldBase
from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _
from south.modelsinspector import add_introspection_rules
from django.core.serializers.json import DjangoJSONEncoder
import json


add_introspection_rules([], ["^cred\.fields\.SizedFileField"])


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
                raise forms.ValidationError(_('File size must be under %(maximumsize)s. Current file size is %(currentsize)s.') % {'maximumsize': filesizeformat(self.max_upload_size), 'currentsize': filesizeformat(data.size)})
        except AttributeError:
            pass

        return data


class JSONField(TextField):
    """JSONField is a generic textfield that neatly serializes/unserializes
    JSON objects seamlessly"""

    # Used so to_python() is called
    __metaclass__ = SubfieldBase

    def to_python(self, value):
        """Convert our string value to JSON after we load it from the DB"""

        if value == "":
            return None

        try:
            if isinstance(value, basestring):
                return json.loads(value)
        except ValueError:
            pass

        return value

    def get_db_prep_save(self, value):
        """Convert our JSON object to a string before we save"""

        if value == "":
            return None

        if isinstance(value, dict):
            value = json.dumps(value, cls=DjangoJSONEncoder)

        return super(JSONField, self).get_db_prep_save(value)
