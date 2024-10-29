import re


class DataStructureUtils:

    def camel_to_snake(self, name):
        return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()

    def json_to_dict(self, data: dict):
        """
        This accepts JSON data. This was created mainly for
        converting camel case variables from the frontend to
        snake case valid for python variables in the backend
        """

        python_dict = {self.camel_to_snake(key): value for key, value in data.items()}

        return python_dict
