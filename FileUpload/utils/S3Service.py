import os
from collections import defaultdict

import boto3
from dotenv import load_dotenv

load_dotenv()

bucket_name = os.environ.get("BUCKET_NAME")
aws_access_key = os.environ.get("AWS_ACCESS_KEY")
aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")


class S3Service:
    def __init__(self):
        s3 = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.s3 = s3
        self.bucket_name = bucket_name

    def create_folder(self, folder_name):
        try:
            self.s3.put_object(Bucket=self.bucket_name, Key=(folder_name + "/"))
            print(f"Created folder {folder_name} in s3://{self.bucket_name}")
        except Exception as e:
            print(f"Error creating folder {folder_name}: {e}")

    def upload_file_to_folder(self, object, folder_path, file_name):
        try:
            self.s3.put_object(
                Body=object, Bucket=self.bucket_name, Key=f"{folder_path}{file_name}"
            )

            print(f"Uploaded {object} to s3://{self.bucket_name}/{file_name}")

            return True
        except Exception as e:
            print(f"Error uploading {object}: {e}")

    def get_object_details(self, bucket_name, object_key):
        try:
            response = self.s3.head_object(Bucket=bucket_name, Key=object_key)

            object_details = {
                "file_size": response["ContentLength"],
                "last_modified": response["LastModified"],
                "content_type": response["ContentType"],
                "etag": response["ETag"],
            }

            return object_details

        except Exception as e:
            print("Error:", e)

    def delete_file(self, bucket_name, object_key):
        try:
            self.s3.delete_object(Bucket=bucket_name, Key=object_key)
            return f"Deleted file '{object_key}' from '{bucket_name}'"
        except Exception as e:
            return f"Error deleting file '{object_key}': {e}"

    def delete_folder(self, bucket_name, folder_prefix):
        try:
            response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

            if "Contents" in response:
                objects_to_delete = [
                    {"Key": obj["Key"]} for obj in response["Contents"]
                ]

                response = self.s3.delete_objects(
                    Bucket=bucket_name, Delete={"Objects": objects_to_delete}
                )

            if "Deleted" in response:
                deleted_objects = response["Deleted"]
                for deleted_obj in deleted_objects:
                    return f"Deleted object '{deleted_obj['Key']}'"
            else:
                return "No objects found in the specified folder."
        except Exception as e:
            return f"Error deleting folder: {e}"

    def list_s3_objects(self, bucket_name, org_id):
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=str(org_id) + "/")

        # Process the objects and create a hierarchical structure
        hierarchical_data = {}

        for item in response.get("Contents", []):
            # Split the object key into segments (folders and file)
            segments = item["Key"].split("/")
            segmentContainsFile = item["Key"][-1] != "/"

            # Initialize a reference to the current level of the hierarchy
            current_level = hierarchical_data

            # Iterate through segments to build hierarchy
            full_path = ""
            i = 1
            for segment in segments:
                if len(segments) == i and segmentContainsFile:
                    full_path += segment
                else:
                    full_path += segment + "/"

                if segment not in current_level:
                    current_level[segment] = {"_path": full_path}
                current_level = current_level[segment]

                i += 1
        jstree_data = self.convert_to_jstree(hierarchical_data)

        return jstree_data

    def get_folders(self, bucket_name, org_id):
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=str(org_id) + "/")

        folders = [{"value": "all", "key": str(org_id) + "/", "name": "All"}]
        for item in response.get("Contents", []):
            if item["Key"][-1] == "/":  # Checking if key is a folder
                folder_name = item["Key"].split("/")[-2]

                folder_value = self.convert_to_camel_case(folder_name)

                if folder_name != org_id:
                    folders.append(
                        {"value": folder_value, "key": item["Key"], "name": folder_name}
                    )

        return folders

    def check_folder_has_files(self, bucket_name, key):
        response = self.s3.list_objects_v2(Bucket=bucket_name, Prefix=key)

        file_count = 0
        for item in response.get("Contents", []):
            if item["Key"][-1] != "/":
                file_count += 1

        folder_contains_files = file_count > 0

        return folder_contains_files

    # Converting the folder name into a camel case format
    def convert_to_camel_case(self, item):
        words = item.split()
        words = [words[0].lower()] + [word.capitalize() for word in words[1:]]
        result = "".join(words)

        return result

    # Function to recursively convert the hierarchical structure into a format suitable for JS Tree
    def convert_to_jstree(self, node):
        jstree_data = []

        id = 0
        for key, value in node.items():
            if len(key) > 0:
                if key == "_path":
                    continue
                containsFile = value["_path"][-1] != "/"
                if containsFile:
                    entry = {
                        "text": key,
                        "dir": self.convert_to_camel_case(key),
                        "object_key": value["_path"],
                        "type": "file",
                        "icon": "https://img.icons8.com/?size=16&id=64965&format=png",
                    }
                else:
                    entry = {
                        "text": key,
                        "dir": self.convert_to_camel_case(key),
                        "object_key": value["_path"],
                        "type": "folder",
                        "icon": "https://img.icons8.com/?size=16&id=WWogVNJDSfZ5&format=png",
                    }
                if "_path" in value:
                    entry["children"] = self.convert_to_jstree(value)
                jstree_data.append(entry)

            id += 1
        return jstree_data
