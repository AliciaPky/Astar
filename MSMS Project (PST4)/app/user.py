# User
class User:
    """
    A base class for all user types in the music school system.

    Attributes:
    - id (int): Unique identifier for the user.
    - name (str): Full name of the user.
    """
    def __init__(self, user_id, name):
        """
        Initializes a User object.

        Parameters:
        - user_id (int): The user's unique ID.
        - name (str): The user's full name.
        """
        self.id = user_id
        self.name = name

    def display_info(self):
        """
        Returns a formatted string with the user's ID and name.

        Returns:
        - str: A string showing user details.
        """
        return f"ID: {self.id} Username: {self.name}"