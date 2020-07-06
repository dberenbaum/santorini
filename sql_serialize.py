from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import serialize


Base = declarative_base()


class State(Base):
    __tablename__ = "states"

    state = Column(String, primary_key=True)
    tries = Column(Integer)
    wins = Column(Integer)


class SQLTree(serialize.Tree):

    def __init__(self, cnxn_str="sqlite:///santorini.db"):
        self.engine = create_engine(cnxn_str)
        self.session = sessionmaker(bind=self.engine)()

    def __enter__(self):
        Base.metadata.create_all(self.engine)
        return self

    def __exit__(self, type, value, traceback):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()

    def __contains__(self, state):
        if self.session.query(State).filter_by(state=state).one_or_none():
            return True
        else:
            return False

    def __getitem__(self, state):
        try:
            sql_state = self.session.query(State).filter_by(state=state).one()
            return sql_state.__dict__
        except:
            raise KeyError

    def insert_state(self, state):
        sql_state = State(state=state, tries=0, wins=0)
        self.session.add(sql_state)
        return sql_state

    def _add_try(self, state):
        sql_state = self.session.query(State).filter_by(state=state).one()
        sql_state.tries += 1

    def add_win(self, state):
        sql_state = self.session.query(State).filter_by(state=state).one()
        sql_state.wins += 1
