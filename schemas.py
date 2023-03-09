from marshmallow import EXCLUDE, Schema, fields, validate as v

status_states = ('subscribed', 'unsubscribed', 'cleaned',
                 'pending', 'transactional', 'archived')


class ExternalMemberMergeFieldsSchema(Schema):
    FNAME = fields.Str()
    LNAME = fields.Str()


class ExternalMemberSchema(Schema):
    id = fields.Str()
    email_address = fields.Str()
    full_name = fields.Str()
    status = fields.Str(validate=v.OneOf(status_states))
    merge_fields = fields.Nested(
        ExternalMemberMergeFieldsSchema, unknown=EXCLUDE)


class MemberSchema(Schema):
    id = fields.Str()
    firstname = fields.Str(attribute="merge_fields.FNAME")
    lastname = fields.Str(attribute="merge_fields.LNAME")
    email = fields.Str(attribute="email_address")
    status = fields.Str(validate=v.OneOf(status_states))
