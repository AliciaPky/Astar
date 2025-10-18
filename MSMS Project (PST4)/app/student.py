#Student
from app.user import User

class StudentUser(User):
    """
    Represents a student in the music school system.
    Inherits from the base User class.
    """
    def __init__(self, id, name, enrolled_course_ids=None):
        """
        Initializes a StudentUser object.

        Parameters:
        - id (int): Unique student ID.
        - name (str): Full name of the student.
        - enrolled_course_ids (list[int], optional): List of course IDs the student is enrolled in.
        """
        super().__init__(id, name)
        self.enrolled_course_ids = enrolled_course_ids  if enrolled_course_ids is not None else []
        
