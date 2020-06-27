import core
import human_play
import random_play
import monte_carlo
import serialize
import json_serialize
import mongo_serialize
import sql_serialize


class PlayerFactory:
    def get_player(self, player_type, name, pawns=None, **kwargs):
        if not pawns:
            pawns = (core.Pawn(), core.Pawn())
        if player_type == "human":
            return human_play.HumanPlayer(name, pawns, **kwargs)
        if player_type == "random":
            return random_play.RandomPlayer(name, pawns, **kwargs)
        if player_type == "monte_carlo":
            return monte_carlo.MonteCarloPlayer(name, pawns, **kwargs)
        else:
            return ValueError(player_type)


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


player_factory = PlayerFactory()
serializer_factory = SerializerFactory()
