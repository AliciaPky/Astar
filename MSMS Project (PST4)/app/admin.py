# Admin

class AdminUser:
    def __init__(self, id, username, password):
        """
        Initializes an AdminUser object.

        Parameters:
        - id (int): Unique identifier for the admin.
        - username (str): Admin's username.
        - password (str): Admin's password.
        """
        self.id = id
        self.username = username
        self.password = password 

    def authenticate(self, input_username, input_password):
        """
        Verifies login credentials.

        Parameters:
        - input_username (str): Username entered by the user.
        - input_password (str): Password entered by the user.

        Returns:
        - bool: True if credentials match, False otherwise.
        """
        """Returns True if credentials match; False otherwise."""
        return self.username == input_username and self.password == input_password

    def __repr__(self):
        """
        Provides a string representation of the AdminUser object.

        Returns:
        - str: Formatted representation with username.
        """
        return f"<AdminUser username={self.username}>"
