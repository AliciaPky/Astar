# Staff

class StaffUser:
    """Represents a staff member in the schedule manager system."""
    
    def __init__(self, id, name, password):
        """
        Initializes a new staff member.
        
        Args:
            staff_id (int): Unique identifier for the staff member.
            username (str): Username for the staff member.
            password (str): Password for the staff member.
        """
        self.id = id
        self.name = name
        self.password = password

    def authenticate(self, input_name, input_password):
        """Authenticates the staff member by comparing the input credentials."""
        return self.name == input_name and self.password == input_password

    def __repr__(self):
        """Returns a string representation of the staff member."""
        return f"<StaffUser username={self.name}>"