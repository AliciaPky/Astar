# Teacher
from app.user import User

class TeacherUser(User):
    """Represents a teacher, extending the User class with a speciality."""
    def __init__(self, id, name, speciality, username, password):
        """
        Initializes a TeacherUser object.

        Parameters:
        - id (int): Unique ID for the teacher.
        - name (str): Full name of the teacher.
        - speciality (str): The teacher's area of expertise.
        """
        super().__init__(id, name)
        self.id = id
        self.speciality = speciality
        self.username = username
        self.password = password
        
    def display_info(self):
        """
        Returns a string containing the teacher's information.

        Returns:
        - str: Basic user info + speciality.
        """
        return f"{super().display_info()}, Speciality: {self.speciality}"
    
    def authenticate(self, input_name, input_password):
        """Authenticates the staff member by comparing the input credentials."""
        return self.name == input_name and self.password == input_password

class Course:
    """Represents a single course offered by the school, linked to a teacher."""
    def __init__(self, id, exam_body, subject, teacher_id, enrolled_student_ids=None, lessons = None):
        """
        Initializes a Course object.

        Parameters:
        - id (int): Unique ID of the course.
        - name (str): Name/title of the course.
        - instrument (str): Instrument focus of the course.
        - teacher_id (int): ID of the teacher assigned to the course.
        - enrolled_student_ids (list[int], optional): List of student IDs enrolled in the course.
        - lessons (list[dict], optional): List of lesson dictionaries associated with the course.
        """
        self.id = id
        self.exam_body = exam_body          # e.g., "SPM", "IGCSE", "UPSR"
        self.subject = subject              # e.g., "Mathematics"
        self.teacher_id = teacher_id        # Linked teacher
        # TODO: Initialize two empty lists: 'enrolled_student_ids' and 'lessons'.
        self.enrolled_student_ids = enrolled_student_ids if enrolled_student_ids is not None else []
        self.lessons = lessons if lessons is not None else []
        # This will hold lesson dictionaries

    def add_lesson(self, title, day, time, duration_minutes):
        """
        Adds a lesson to the course schedule.

        Parameters:
        - title (str): Lesson title.
        - day (str): Day of the week (e.g., 'Monday').
        - time (str): Time of the lesson (e.g., '14:00').
        - duration_minutes (int): Duration of the lesson in minutes.
        """
        lesson = {
            "title": title,
            "day": day,
            "time": time,
            "duration": duration_minutes
        }
        self.lessons.append(lesson)
        print(f"Added lesson '{title}' on {day} at time {time} for ({duration_minutes} mins) to course {self.name}.")
