from south.modelsinspector import add_introspection_rules

from famille.utils import fields as extra_fields

from .users import *
from .planning import *
from .rating import *
from .misc import *

# south rules
add_introspection_rules(extra_fields.content_type_restricted_file_field_rules, ["^famille\.utils\.fields", ])
