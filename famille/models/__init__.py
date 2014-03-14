from south.modelsinspector import add_introspection_rules

from famille.utils import fields as extra_fields

from .users import Famille, Prestataire, Enfant, get_user_related, Reference
from .planning import FamillePlanning, PrestatairePlanning

# south rules
add_introspection_rules(extra_fields.content_type_restricted_file_field_rules, ["^famille\.utils\.fields", ])
