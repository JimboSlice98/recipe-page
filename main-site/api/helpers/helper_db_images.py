import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import (redirect, render_template, request, 
                   url_for)

# from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from azure.data.tables import TableServiceClient, TableClient

load_dotenv()

class ImageStorageManager:
    def __init__(self):
        try:
            self.IMAGE_STORAGE_CONNECTION_STRING = os.getenv('IMAGE_STORAGE_CONNECTION_STRING')
            self.IMAGE_STORAGE_CONTAINER_NAME = os.getenv('IMAGE_STORAGE_CONTAINER_NAME')
            self.IMAGE_STORAGE_ACCOUNT_NAME = os.getenv('IMAGE_STORAGE_ACCOUNT_NAME')
            self.IMAGE_STORAGE_TABLE_NAME = os.getenv('IMAGE_STORAGE_TABLE_NAME')

            self.table_service_client = TableServiceClient.from_connection_string(conn_str=self.IMAGE_STORAGE_CONNECTION_STRING)
            self.table_client = self.table_service_client.get_table_client(table_name=self.IMAGE_STORAGE_TABLE_NAME)
            self.blob_service_client = BlobServiceClient.from_connection_string(self.IMAGE_STORAGE_CONNECTION_STRING)
        
        except Exception as e:
            print(f"An error occurred during initialization: {e}")

    def fetch_images_metadata(self, user_id, blog_id):
        images_metadata = {blog_id: []}
        try:
            blob_table_client = TableClient.from_connection_string(conn_str=self.IMAGE_STORAGE_CONNECTION_STRING, table_name=self.IMAGE_STORAGE_TABLE_NAME)
            query_filter = f"PartitionKey eq '{user_id}' and BlogId eq '{blog_id}'"
            entities = blob_table_client.query_entities(query_filter)
            
            for entity in entities:
                images_metadata[blog_id].append(entity)
        except Exception as e:
            print(f"Error fetching entities: {e}")

        return images_metadata

    def generate_blob_urls_by_blog_id(self, images_metadata):
        blob_urls_by_blog_id = {}
        try:
            for blog_id, metadata_list in images_metadata.items():
                blob_urls_by_blog_id[blog_id] = []

                for metadata in metadata_list:
                    extension = metadata['Extension']
                    unique_id = metadata['RowKey']
                    user_id = metadata['PartitionKey']

                    # Construct the blob name and URL
                    filename = f"{unique_id}_{user_id}{extension}{blog_id}"
                    blob_url = f"https://{self.IMAGE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{self.IMAGE_STORAGE_CONTAINER_NAME}/{filename}"
                    blob_urls_by_blog_id[blog_id].append(blob_url)
        
        except Exception as e:
            print(f"An error occurred while generating blob URLs: {e}")
        
        return blob_urls_by_blog_id

    def upload_image_to_blob(self, unique_filename, file):
        """
        Uploads a local file to Azure Blob Storage.
        """
        conn_Str = self.IMAGE_STORAGE_CONNECTION_STRING
        print("here\n", conn_Str)
        try:
            
            blob_service_client = BlobServiceClient.from_connection_string(conn_Str)
            
            # Create the container if it doesn't exist
            # container_client = blob_service_client.get_blob_client(container=ImageStorageManager.IMAGE_STORAGE_CONTAINER_NAME, blob=unique_filename)
            # try:
            #     container_client.create_container()
            # except Exception as e:
            #     print(f"Container already exists or another error occurred: {e}")
        except:
            print("couldnt connect to the image storage")
        print("blobl uplodad", "connected to blob client")

        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=self.IMAGE_STORAGE_CONTAINER_NAME, blob=unique_filename)
        print("blobl uplodad", "got blob id")

        # Upload the local file to blob storage
        blob_client.upload_blob(file, blob_type="BlockBlob", overwrite=True)

        print("blobl uplodad", "file", unique_filename)
        
        # print(f"File {upload_file_path} uploaded to {container_name}/{blob_name}")


    def delete_image_from_blob(self, blob_name):
        try:
            # Create a blob client
            # blob_client = BlobServiceClient.from_connection_string(IMAGE_STORAGE_CONNECTION_STRING).get_blob_client(container=container_name, blob=blob_name)
        
            blob_client = self.blob_service_client.get_blob_client(container=self.IMAGE_STORAGE_CONTAINER_NAME, blob=blob_name)
            blob_client.delete_blob()
            print(f"Blob {blob_name} deleted successfully.")
        except Exception as e:
            print(f"Failed to delete blob: {e}")

    def get_blob_sas_url(self, blob_name):
        try:
            blob_client = self.blob_service_client.get_blob_client(container=self.IMAGE_STORAGE_CONTAINER_NAME, blob=blob_name)
            sas_token = generate_blob_sas(account_name=self.IMAGE_STORAGE_ACCOUNT_NAME,
                                          container_name=self.IMAGE_STORAGE_CONTAINER_NAME,
                                          blob_name=blob_name,
                                          account_key=self.blob_service_client.credential.account_key,
                                          permission=BlobSasPermissions(read=True),
                                          expiry=datetime.utcnow() + timedelta(hours=1))
            blob_url_with_sas = f"https://{self.IMAGE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{self.IMAGE_STORAGE_CONTAINER_NAME}/{blob_name}?{sas_token}"
            return blob_url_with_sas
        except Exception as e:
            print(f"Failed to generate SAS URL: {e}")
            return "failed"


    def delete_image_metadata(self, user_id, unique_id):
        try:
            self.table_client.delete_entity(partition_key=str(user_id), row_key=str(unique_id))
            print(f"Metadata for {unique_id} deleted successfully.")
        except Exception as e:
            print(f"Failed to delete metadata: {e}")


    # Is this function ever used?
    def get_image_metadata(self, storage_connection_string, user_id, unique_id):
        try:
            table_client = TableClient.from_connection_string(conn_str=storage_connection_string, table_name="ImageMetadata")
            entity = table_client.get_entity(partition_key=str(user_id), row_key=unique_id)
            return entity
        except Exception as e:
            print(f"Entity could not be found: {e}")
            return None

    @staticmethod
    def generate_unique_filename(original_filename, user_id=1, blog_id=1):
        extension = os.path.splitext(original_filename)[1]
        unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{unique_id}_{user_id if user_id else 'guest'}{extension}{blog_id}"
        return filename, unique_id
    
    
    def insert_image_metadata(self, user_id, blog_id, original_filename, date):

        storage_connection_string = self.IMAGE_STORAGE_CONNECTION_STRING
        # Generate unique parts of the filename
        unique_id = date
        extension = os.path.splitext(original_filename)[1]
        # unique_id = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{unique_id}_{user_id if user_id else 'guest'}{blog_id}{extension}"

        # Create a table client
        try:
            table_client = TableClient.from_connection_string(conn_str=storage_connection_string, table_name=self.IMAGE_STORAGE_TABLE_NAME)
        except:
            print("failed to connect: insert_image_metadata")
            return redirect(url_for('404'))

        # Define the entity to insert
        entity = {
            "PartitionKey": str(user_id),
            "RowKey": unique_id,
            "BlogId": str(blog_id),
            "OriginalFilename": original_filename,
            "Extension": extension,
            "Timestamp": datetime.now()
        }

        # Insert the entity
        table_client.create_entity(entity=entity)
        print("finished inserting image metadata")

        return filename

