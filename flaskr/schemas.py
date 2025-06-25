from marshmallow import Schema, fields, validate, pre_load

class ServerSchema(Schema):
    id          = fields.Int(dump_only=True)
    name        = fields.Str(required=True, validate=validate.Length(min=1, max=128))
    ip_address  = fields.Str(
                     required=True,
                     validate=validate.Regexp(
                       r"^((25[0-5]|2[0-4]\d|[01]?\d\d?)(\.|$)){4}$",
                       error="Invalid IPv4 address"
                     )
                  )
    description = fields.Str(validate=validate.Length(max=500), allow_none=True)
    user_id     = fields.Int(required=True)

    @pre_load
    def alias_ip(self, data, **kwargs):
        if 'ip' in data and 'ip_address' not in data:
            data['ip_address'] = data.pop('ip')
        return data

class SkinSchema(Schema):
    id          = fields.Int(dump_only=True)
    server_id   = fields.Int(required=True)
    name        = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    # Zmienione na Str, by 'url1' było akceptowane
    image_url   = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str(validate=validate.Length(max=500), allow_none=True)

class VoteSchema(Schema):
    server_id   = fields.Int(required=True)
    ip_address  = fields.Str(
                     required=True,
                     validate=validate.Regexp(
                       r"^((25[0-5]|2[0-4]\d|[01]?\d\d?)(\.|$)){4}$",
                       error="Invalid IPv4 address"
                     )
                  )
