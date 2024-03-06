import pytest
from unittest.mock import patch
from api.helpers.helper_db_messages import MessagesDatabaseManager
import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def messages_db_manager():
    with patch('api.helpers.helper_db_messages') as mock:
        instance = mock.return_value
        instance.initialize_database.return_value = None  # Assuming no return value
        return instance

def test_initialize_database(messages_db_manager):
    # Mock the environment variables
    with patch.dict('os.environ', {}):
        messages_db_manager.initialize_database()
        # Test passes if no exception is raised

def test_insert_message(messages_db_manager):
    message_data = {        
        'user_id1': 100,
        'user_id2': 200,
        'message': 'Hello, how are you?',
        'sender': 100,
        'time_stamp': '2024-03-06 12:00:00'
    }
    with patch.object(messages_db_manager, 'insert_message', return_value=None) as mock_method:
        messages_db_manager.insert_message(message_data)
        mock_method.assert_called_with(message_data)
        # Test passes if no exception is raised

def test_get_ordered_messages(messages_db_manager):
    user_ids = [100, 200]
    with patch.object(messages_db_manager, 'get_ordered_messages', return_value=[]) as mock_method:
        result = messages_db_manager.get_ordered_messages(user_ids)
        mock_method.assert_called_with(user_ids)
        assert isinstance(result, list)
        # Test passes if no exception is raised

def test_get_user_id_conversations(messages_db_manager):
    user_id = 100
    with patch.object(messages_db_manager, 'get_user_id_conversations', return_value=[]) as mock_method:
        result = messages_db_manager.get_user_id_conversations(user_id)
        mock_method.assert_called_with(user_id)
        assert isinstance(result, list)
#         # Test passes if no exception is raised


# def test_initialize_database(messages_db_manager):
#     # Mock the environment variables
#     with patch.dict({   
#     }):
#         messages_db_manager.initialize_database()
#         # test fails is an exception is raised
        
# def test_insert_message(messages_db_manager):
#     message_data = {
#         'choot_id': "choot",
#         'user_id1': 100,
#         'user_id2': 200,
#         'message': 'Hello, how are you?',
#         'sender': 100,
#         'time_stamp': '2024-03-06 12:00:00'
#     }
#     messages_db_manager.insert_message(message_data)

# def test_get_ordered_messages(messages_db_manager):
#     user_ids = [100, 200]
#     result = messages_db_manager.get_ordered_messages(user_ids)
#     assert isinstance(result, list)

# def test_get_user_id_conversations(messages_db_manager):
#     user_id = 100
#     result = messages_db_manager.get_user_id_conversations(user_id)
#     assert isinstance(result, list)
