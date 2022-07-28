import json
import os
import random

import requests
from django.conf import settings

API_BASE_URL = settings.API_BASE_URL

class JsonConnector:
    """
        handles json files.
    """
    data = ['no']
    def __init__(self, filepath):
        self.file = filepath
        with open(filepath) as f:
            data = json.loads(f.read())
        self.data = data

    @property
    def parsed_data(self) -> list:
        return self.data

def connection_factory(filepath):
    """
        factory method for initializing JsonConnector
    """
    if filepath.endswith('.json'):
        connector = JsonConnector
    else:
        raise ValueError("Invalid file format. No handler for this file")
    return connector(filepath)

def connect_to(filepath):
    """
        A wrapper function for connection_factory to handle error.
    """
    factory = None
    try:
        factory = connection_factory(filepath)
    except ValueError as err:
        print(err)
    return factory

class ApiConnector:
    """
    1. Iterate through data.
    2. Get questions from every JSON file.
    3. Push Data to the database using the Create Question endpoint.
    """

    def __init__(self, directory, token, category=1, api_base_url=API_BASE_URL):
        self.api_base_url = api_base_url
        self.headers = {'Accept': '*/*', 'Authorization': f"Bearer {token}"}
        self.directory = directory
        self.file_extension = '.json'
        self.category = category

    def run(self):
        """
            initialize the process of posting the data to the db.
        """
        files = self.get_list_of_json_files()
        self.send_data_to_api(files)

    def get_list_of_json_files(self) -> list:
        """
            gather all json files in the directory inside a list
        """
        list_of_only_files = [dirs_or_files for dirs_or_files in os.listdir(
            self.directory) if os.path.isfile(f"{self.directory}/{dirs_or_files}")]
        return [file for file in list_of_only_files if file.endswith(self.file_extension)]

    def format_data_for_api(self, data: dict)-> dict:
        """
            returns a ready made body to use as json payload in the request body
        """
        type = "multiple-choice" if len(data.get('incorrect answers')) > 1 else "True / False"
        try:
            incorrect_answer_fields = {
                "incorrect_answer_1": data.get('incorrect answers')[0]
            }
            if type == "multiple-choice":
                incorrect_answer_fields.setdefault("incorrect_answer_2", data.get('incorrect answers')[1])
                incorrect_answer_fields.setdefault("incorrect_answer_3", data.get('incorrect answers')[2])
        except Exception as err:
            print("This data:", data, "caused the error")
            print(err)
        else:
            formatted_data = {
                'question': data.get('question'),
                'difficulty': random.choice(['eazy', 'medium', 'hard']),
                'type': type,
                'category': self.category,
                'correct_answer': data.get('correct_answer'),
                'incorrect_answer_fields': incorrect_answer_fields,
                'explanation': data.get("explanation")
                }
            return formatted_data

    def send_data_to_api(self, files: list):
        """
            actually send data to the api endpoint.
        """
        for file in files:
            list_of_data = connect_to(os.path.join(self.directory, file)).parsed_data
            for data in list_of_data:
                body = self.format_data_for_api(data)
                self.post_data_to_api(body)   

    def post_data_to_api(self, data):
        """
            handles sending of data to the api endpoint.
        """
        link = f"{self.api_base_url}questions/"
        r = requests.post(link, json=data, headers=self.headers)
        if r.status_code == 201:
            return "success"
        return "failed"

DIRECTORY = f"{os.path.dirname(os.path.abspath(__file__))}\data\microbiology"
token = settings.ADMIN_TOKEN
def main():
    api = ApiConnector(DIRECTORY, token)
    api.run()


if __name__ == '__main__':
    main()
