import pytest
from unittest.mock import patch

import pytest
from api.helpers.helper_db_images import ImageStorageManager

@pytest.fixture
def image_storage_manager():
    return ImageStorageManager()

# def test_upload_image_to_blob(image_storage_manager):
#     image_storage_manager.upload_image_to_blob("test.jpg", "path_to_image.jpg")

def test_delete_image_from_blob(image_storage_manager):
    image_storage_manager.delete_image_from_blob("test.jpg")

def test_delete_image_metadata(image_storage_manager):
    image_storage_manager.delete_image_metadata("user123", "unique_id123")

def test_generate_unique_filename():
    ImageStorageManager.generate_unique_filename("test.jpg")

@patch('api.helpers.helper_db_images.TableClient')
def test_insert_image_metadata(mock_table_client, image_storage_manager):
    mock_create_entity = mock_table_client.return_value.create_entity
    mock_create_entity.return_value = None

    result = image_storage_manager.insert_image_metadata("user123", "blog_id123", "test.jpg", "2024-03-06")

    assert result != ""
