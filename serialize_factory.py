import serialize
import json_serialize
import mongo_serialize
import sql_serialize


class SerializerFactory:
    def get_serializer(self, format, **kwargs):
        if not format:
            return serialize.Tree()
        if format == "json":
            return json_serialize.JsonTree(**kwargs)
        if format == "sql":
            return sql_serialize.SQLTree(**kwargs)
        if format == "mongo":
            return mongo_serialize.MongoTree(**kwargs)
        else:
            return ValueError(format)


serializer_factory = SerializerFactory()
