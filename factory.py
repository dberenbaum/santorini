import core
import human_play
import ai_play
import serialize
import json_serialize
import mongo_serialize
import sql_serialize


class PlayerFactory:
    def get_player(self, player_type, name, **kwargs):
        if player_type == "human":
            return human_play.HumanPlayer(name, **kwargs)
        if player_type == "random":
            return ai_play.RandomPlayer(name, **kwargs)
        if player_type == "epsilon_greedy":
            return ai_play.EpsilonGreedyPlayer(name, **kwargs)
        if player_type == "uct":
            return ai_play.UCTPlayer(name, **kwargs)
        if player_type == "mcts":
            return ai_play.MCTSPlayer(name, **kwargs)
        if player_type == "cnn":
            return ai_play.CNNPlayer(name, **kwargs)
        if player_type == "mcts_cnn":
            return ai_play.MctsCnnPlayer(name, **kwargs)
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
