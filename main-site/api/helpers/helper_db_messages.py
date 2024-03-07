import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, select, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import psycopg2

from dotenv import load_dotenv


load_dotenv()

class MessagesDatabaseManager:
    metadata = MetaData()
    messages = Table('messages', metadata,
                    Column('chat_id', Integer, primary_key=True),
                    Column('user_id1', Integer),
                    Column('user_id2', Integer),
                    Column('message', Text),
                    Column('sender', Integer),
                    Column('time_stamp', Text))
    

    @classmethod
    def initialize_database(cls):
        try:
            DATABASE_URL = (
                f"postgresql://{os.environ['MESSAGING_DB_USER']}:{os.environ['MESSAGING_DB_PASSWORD']}@"
                f"{os.environ['MESSAGING_DB_HOST']}:{os.environ['MESSAGING_DB_PORT']}/{os.environ['MESSAGING_DB_NAME']}?sslmode={os.environ['MESSAGING_DB_SSLMODE']}"
            )
            cls.engine = create_engine(DATABASE_URL)
            cls.metadata.bind = cls.engine
            cls.Session = sessionmaker(bind=cls.engine)
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise 


    @staticmethod
    def insert_message(message_data):
        session = MessagesDatabaseManager.Session()
        try:
            new_message = MessagesDatabaseManager.messages.insert().values(**message_data)
            session.execute(new_message)
            session.commit()
            print(f"Inserted message from user {message_data['user_id1']} to user {message_data['user_id2']}")
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")
            session.rollback()
        finally:
            session.close()


    @staticmethod
    def get_ordered_messages(user_ids):
        session = MessagesDatabaseManager.Session()
        try:
            user_id1, user_id2 = user_ids[0], user_ids[1]
            query = select(MessagesDatabaseManager.messages).where(
                or_(
                    (MessagesDatabaseManager.messages.c.user_id1 == user_id1) & (MessagesDatabaseManager.messages.c.user_id2 == user_id2),
                    (MessagesDatabaseManager.messages.c.user_id1 == user_id2) & (MessagesDatabaseManager.messages.c.user_id2 == user_id1)
                )
            ).order_by(MessagesDatabaseManager.messages.c.time_stamp.asc())
            result = session.execute(query).fetchall()
            return list(result)
        finally:
            session.close()


    @staticmethod
    def get_user_id_conversations(user_id1):
        session = MessagesDatabaseManager.Session()
        try:
            subquery1 = select(MessagesDatabaseManager.messages.c.user_id2).where(MessagesDatabaseManager.messages.c.user_id1 == user_id1).distinct()
            subquery2 = select(MessagesDatabaseManager.messages.c.user_id1).where(MessagesDatabaseManager.messages.c.user_id2 == user_id1).distinct()
            query = subquery1.union(subquery2)
            result = session.execute(query).fetchall()
            return [a_result[0] for a_result in result]
        finally:
            session.close()
