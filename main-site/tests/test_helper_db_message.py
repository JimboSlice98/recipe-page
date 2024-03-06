import pytest
from unittest.mock import patch
from api.helpers.helper_db_messages import MessagesDatabaseManager

@pytest.fixture
def messages_db_manager():
    MessagesDatabaseManager.initialize_database()
    return MessagesDatabaseManager


def test_initialize_database(messages_db_manager):
    # Mock the environment variables
    with patch.dict('os.environ', {
        'DB_USER': 'test_user',
        'DB_PASSWORD': 'test_password',
        'DB_HOST': 'test_host',
        'DB_PORT': '5432',
        'DB_NAME': 'test_db',
        'DB_SSLMODE': 'require'
    }):
        messages_db_manager.initialize_database()
        assert messages_db_manager.engine is not None
        assert messages_db_manager.Session is not None

def test_insert_message(messages_db_manager):
    message_data = {
        'chat_id': 1,
        'user_id1': 100,
        'user_id2': 200,
        'message': 'Hello, how are you?',
        'sender': 100,
        'time_stamp': '2024-03-06 12:00:00'
    }
    messages_db_manager.insert_message(message_data)

def test_get_ordered_messages(messages_db_manager):
    user_ids = [100, 200]
    result = messages_db_manager.get_ordered_messages(user_ids)
    assert isinstance(result, list)

def test_get_user_id_conversations(messages_db_manager):
    user_id = 100
    result = messages_db_manager.get_user_id_conversations(user_id)
    assert isinstance(result, list)
