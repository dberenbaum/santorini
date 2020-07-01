import core
import human_play
import random_play
import monte_carlo
import serialize
import json_serialize
import mongo_serialize
import sql_serialize


class PlayerFactory:
    def get_player(self, player_type, name, **kwargs):
        if player_type == "human":
            return human_play.HumanPlayer(name, **kwargs)
        if player_type == "random":
            return random_play.RandomPlayer(name, **kwargs)
        if player_type == "epsilon_greedy":
            return monte_carlo.EpsilonGreedyPlayer(name, **kwargs)
        if player_type == "monte_carlo":
            return monte_carlo.MonteCarloPlayer(name, **kwargs)
        if player_type == "mcts":
            return monte_carlo.MCTSPlayer(name, **kwargs)
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
        if format == "mongo_bulk":
            return mongo_serialize.BulkMongoTree(**kwargs)
        else:
            return ValueError(format)


player_factory = PlayerFactory()
serializer_factory = SerializerFactory()
