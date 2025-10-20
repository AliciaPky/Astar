# Schedule
import json
import csv
import datetime
from app.student import StudentUser
from app.teacher import TeacherUser, Course
from app.admin import AdminUser
from app.staff import StaffUser
import os
import shutil 



class ScheduleManager:
    """Main controller for all business logic and data handling across MSMS."""

    def __init__(self, data_path="data/msms.json", log_path="data/system_log.txt", backup_path="data/backup_data.json"):
        """
        Initializes the ScheduleManager by loading persisted data or creating defaults.

        - Sets up internal storage for all users, instruments, and courses.
        - Initializes ID counters to avoid duplication when creating new entities.
        - Loads existing data from JSON file (if available).
        - If no admin user is found, a default admin account is created to prevent lockout.
        """
        self.data_path = data_path  # JSON file path to persist/load data
        self.log_path = log_path    # txt file path to log actions
        self.backup_path = backup_path  # JSON file path to backup data

        # Internal in-memory stores for each entity type
        self.students = []
        self.teachers = []
        self.courses = []
        self.attendance_log = []
        self.instruments = []
        self.admin = []
        self.staff = []
        self.finance_log = []

        # ID counters ensure unique identifiers for each user type
        self.next_student_id = 4000
        self.next_teacher_id = 3000
        self.next_admin_id = 1000
        self.next_staff_id = 2000

        # Attempt to load existing data from disk
        self._load_data()

        # If no admin exists, auto-create a default one to allow login access
        if self.admin == []:
            print("No admin users found. Creating default admin user.")
            self.add_admin("admin", "password")
        
        if not os.path.exists(self.log_path):
            with open(self.log_path, "w") as f:
                f.write("=== System Log Started ===\n")

    def _load_data(self):
        """
        Load data from JSON file safely.
        Handles missing or corrupted files gracefully, logging any error.
        """
        if not os.path.exists(self.data_path):
            self.log_action("LOAD_INFO", f"No data file found at {self.data_path}, starting fresh.")
            self._save_data()  # create empty structure
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load all entity lists
            self.students = [StudentUser(**s) for s in data.get("students", [])]
            self.teachers = [TeacherUser(**t) for t in data.get("teachers", [])]
            self.staff = [StaffUser(**st) for st in data.get("staff", [])]
            self.admins = [AdminUser(**a) for a in data.get("admins", [])]
            self.courses = [Course(**c) for c in data.get("courses", [])]
            self.instruments = data.get("instruments", [])
            self.finance_log = data.get("finance_log", [])
            self.attendance_log = data.get("attendance_log", [])

            self.log_action("LOAD", f"Loaded data from {self.data_path}")

        except json.JSONDecodeError as e:
            #Corrupted file detected
            self.log_action("LOAD_ERROR", f"Corrupted JSON file {self.data_path}: {e}")
            # Optional recovery: rename or back up corrupted file
            backup_corrupt = f"{self.data_path}.corrupt"
            try:
                os.rename(self.data_path, backup_corrupt)
                self.log_action("BACKUP_ERROR", f"Corrupted file backed up as {backup_corrupt}")
            except Exception as rename_err:
                self.log_action("BACKUP_ERROR", f"Failed to back up corrupt file: {rename_err}")

            # Reset data to defaults
            self.students, self.teachers, self.staff, self.admins = [], [], [], []
            self.courses, self.instruments = [], []
            self.finance_log, self.attendance_log = [], []
            self._save_data()

        except Exception as e:
            #Other unexpected error types
            self.log_action("LOAD_ERROR", f"Failed to load data from {self.data_path}: {e}")

    def _save_data(self):
        """
        Saves the current in-memory data to JSON file.
        Uses object __dict__ to serialize custom objects.
        """
        data_to_save = {
            "students": [s.__dict__ for s in self.students],
            "teachers": [t.__dict__ for t in self.teachers],
            "courses": [c.__dict__ for c in self.courses],
            "attendance": self.attendance_log,
            "instruments": self.instruments,
            "admin": [a.__dict__ for a in self.admin],
            "staff": [sa.__dict__ for sa in self.staff],
            "finance_log":self.finance_log,
            "next_student_id": self.next_student_id,
            "next_teacher_id": self.next_teacher_id,
            "next_admin_id": self.next_admin_id,
            "next_staff_id": self.next_staff_id
        }
        try:
            # Attempt to write JSON
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=4)

            # Only log success if dump succeeded
            self.log_action("SAVE", f"Data saved to {self.data_path}")

        except Exception as e:
            # ✅ Catch all errors (e.g., json.dump failures)
            error_msg = f"Error saving data to {self.data_path}: {e}"
            self.log_action("SAVE_ERROR", error_msg)
    
            
            
    def log_action(self, action_type, message):
        """
        Record an event with a timestamp to the system log.

        Args:
            action_type (str): Category of the event.
            message (str): Description of the action performed.
        """
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{action_type}] {message}\n"

        with open(self.log_path, "a", encoding="utf-8") as log_file:
            log_file.write(log_entry)
            
            
    def backup_data(self) -> str:
        """
        Create a manual backup of the current data file.
        This function is only executed when the admin explicitly requests it.

        Returns:
            str: Status message indicating success or failure.
        """
        try:
            # Check if main data file exists
            if os.path.exists(self.data_path):
                shutil.copy(self.data_path, self.backup_path)
                msg = f"Backup created successfully at {self.backup_path}"
                self.log_action("MANUAL_BACKUP", msg)
                return msg
            else:
                msg = f"Backup failed — data file not found at {self.data_path}"
                self.log_action("MANUAL_BACKUP_FAIL", msg)
                return msg

        except Exception as e:
            msg = f"Backup failed due to error: {e}"
            self.log_action("MANUAL_BACKUP_FAIL", msg)
            return msg

    def find_student_by_id(self, student_id):
        """
        Find a student object by its unique ID.
        Returns the StudentUser instance or None if not found.
        """
        return next((s for s in self.students if s.id == student_id), None)

    def find_teacher_by_id(self, teacher_id):
        """
        Find a teacher object by its unique ID.
        Returns the TeacherUser instance or None if not found.
        """
        return next((t for t in self.teachers if t.id == teacher_id), None)

    def find_course_by_id(self, course_id):
        """
        Find a course object by its unique ID.
        Returns the Course instance or None if not found.
        """
        return next((c for c in self.courses if c.id == course_id), None)

    def add_student(self, name):
        """
        Create a new student with an auto-incremented ID and add to students list.
        Save data after addition.
        """
        os.system('cls')
        new_student = StudentUser(self.next_student_id, name)
        self.students.append(new_student)
        self.log_action("ADD_STUDENT", f"Added student: {name} (ID {self.next_student_id})")
        self.next_student_id += 1
        self._save_data()
        print(f"Added student: {new_student.display_info()}")
        
        return new_student

    def add_teacher(self, name, speciality):
        """
        Create a new teacher with auto-incremented ID and add to teachers list.
        Save data after addition.
        """
        os.system('cls')
        new_teacher = TeacherUser(self.next_teacher_id, name, speciality)
        self.teachers.append(new_teacher)
        self.log_action("ADD_TEACHER", f"Added teacher: {name} (ID {self.next_student_id}), Speciality:{speciality}")
        self.next_teacher_id += 1
        self._save_data()
        print(f"Added teacher: {new_teacher.display_info()}")
        
        return new_teacher

    def add_course(self, name, instrument, teacher_id):
        """
        Add a new course associated with a teacher ID.
        Validates teacher existence before adding.
        Course IDs start from 1 and increment with the number of courses.
        """
        os.system('cls')
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            print("Error: Invalid teacher ID.")
            
            return None
        self.log_action("ADD_COURSE", f"Added course: {name}, Instrument: {instrument} (ID: {len(self.courses)}), Teacher ID: {teacher_id}")
        new_id = len(self.courses) + 1  # Simple ID generation based on current count
        new_course = Course(new_id, name, instrument, teacher_id)
        self.courses.append(new_course)
        self._save_data()
        print(f"Added course: {new_course.name} ({new_course.instrument}) by {teacher.name}")
        
        return new_course

    def enroll_student_in_course(self, student_id, course_id):
        """
        Enroll a student into a course.
        Validates student and course existence.
        Prevents duplicate enrollments.
        Saves data after enrollment.
        """
        os.system('cls')
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)

        if not student or not course:
            print("Enrollment failed: Invalid student or course ID.")
            
            return False

        if course_id in student.enrolled_course_ids:
            print(f"{student.name} is already enrolled in {course.name}.")
            
            return False

        student.enrolled_course_ids.append(course_id)
        course.enrolled_student_ids.append(student_id)
        self._save_data()
        print(f"{student.name} enrolled in {course.name}.")
        self.log_action("ENROLL", f"{student.name} enrolled in {course.name}")
        return True

    def check_in_student(self, student_id, course_id):
        """
        Another variant of check-in that also stores the course name.
        """
        os.system('cls')
        student = self.find_student_by_id(student_id)
        course = self.find_course_by_id(course_id)
        
        if not student or not course:
            print("Check-in failed: Invalid student or course ID.")
            
            return False

        timestamp = datetime.datetime.now().isoformat()
        check_in_record = {
            "student_id": student_id,
            "course_id": course_id,
            "course_name": course.name,
            "timestamp": timestamp
        }

        self.attendance_log.append(check_in_record)
        self._save_data()
        print(f"{student.name} checked in at {timestamp}.")
        self.log_action("CHECKIN", f"{student.name} checked in to {course.name}")
        return True

    def get_attendance_log(self):
        """
        Return the full attendance log as a list of check-in dictionaries.
        """
        return self.attendance_log

    def get_daily_roster(self, day):
        """
        Generate a list of scheduled lessons for a given day.
        Validates the day input.
        Returns list of lesson info dictionaries.
        """
        os.system('cls')
        if not isinstance(day, str):
            print("Error: Day must be a string.")
            
            return []

        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day = day.lower().strip()

        if day not in valid_days:
            print("Invalid day name.")
            
            return []

        roster = []
        for course in self.courses:
            for lesson in course.lessons:
                if lesson["day"].lower() == day:
                    teacher = self.find_teacher_by_id(course.teacher_id)
                    teacher_name = getattr(teacher, 'name', 'Unknown') if teacher else 'Unknown'
                    roster.append({
                        "course_name": course.name,
                        "course_id": course.id,
                        "instrument": course.instrument,
                        "teacher_name": teacher_name,
                        "lesson_title": lesson["title"],
                        "time": lesson["time"],
                        "duration": lesson["duration"],
                        "students_enrolled": len(course.enrolled_student_ids)
                    })
        return roster
    
    def switch_student_course(self, student_id, from_course_id, to_course_id):
        """
        Switch a student from one course to another.
        Validates student and both courses.
        Checks enrollment status before switching.
        Saves data after switching.
        """
        os.system('cls')
        student = self.find_student_by_id(student_id)
        from_course = self.find_course_by_id(from_course_id)
        to_course = self.find_course_by_id(to_course_id)

        if not student or not from_course or not to_course:
            print("Switch failed: Invalid student or course ID.")
            
            return False

        if from_course_id not in student.enrolled_course_ids:
            print(f"Switch failed: {student.name} is not enrolled in {from_course.name}.")
            
            return False

        if to_course_id in student.enrolled_course_ids:
            print(f"Switch unnecessary: {student.name} is already enrolled in {to_course.name}.")
            
            return False

        # Perform the switch
        student.enrolled_course_ids.remove(from_course_id)
        from_course.enrolled_student_ids.remove(student_id)

        student.enrolled_course_ids.append(to_course_id)
        to_course.enrolled_student_ids.append(student_id)

        self._save_data()
        print(f"{student.name} switched from {from_course.name} to {to_course.name}.")
        
        return True
    
    def add_admin(self, username, password):
        """
        Add a new admin user with auto-incremented ID.
        Saves data after addition.
        """
        os.system('cls')
        new_admin = AdminUser(self.next_admin_id, username, password)
        self.admin.append(new_admin)
        self.next_admin_id += 1
        self._save_data()
        print(f"Added admin | Name: {new_admin.username} Password: {new_admin.password}")
        self.log_action("ADD_ADMIN", f"Admin created:{username}")
        return new_admin
    
    def find_admin_by_id(self, admin_id):
        """
        Find an admin user by their ID.
        Returns AdminUser or None if not found.
        """
        return next((a for a in self.admin if a.id == admin_id), None)
    
    def add_staff(self, name, password):
        """
        Add a new staff member with auto-incremented ID.
        Saves data after addition.
        """
        os.system('cls')
        new_staff = StaffUser(self.next_staff_id, name, password)
        self.staff.append(new_staff)
        self.next_staff_id += 1
        self._save_data()
        print(f"Added staff | Name: {new_staff.name} Password: {new_staff.password}")
        self.log_action("ADD_STAFF", f"Staff added: {name}")
        return new_staff

    
    def find_staff_by_id(self, staff_id):
        """
        Find a staff member by their unique ID.
        Returns StaffUser or None if not found.
        """
        return next((sa for sa in self.staff if sa.id == staff_id), None)
    
    def add_instrument(self, instrument_name):
        """
        Add a new instrument to the instruments list if not already present.
        Saves data after addition.
        """
        os.system('cls')
        if instrument_name in self.instruments:
            print(f"Instrument '{instrument_name}' already exists.")
            
            return False
        self.instruments.append(instrument_name)
        self._save_data()
        print(f"Added instrument: {instrument_name}")
        self.log_action("ADD_INSTRUMENT", f"Added instrument: {instrument_name}")
        return True
    
    def sign_in_admin(self, username, password):
        """
        Attempt to sign in an admin by checking username and password.
        """
        for admin in self.admin:
            if admin.authenticate(username, password):
                print(f"Welcome, {username}!")
                self.log_action("LOGIN", f"Admin {username} signed in")
                return True
        print("Invalid username or password.")
        self.log_action("LOGIN_FAIL", f"Invalid admin login for {username}")
        return False
    
    def sign_in_staff(self, username, password):
        """
        Attempt to sign in a staff member with username and password.
        """
        for staff in self.staff:
            if staff.name == username and staff.password == password:
                print(f"Welcome, {username}!")
                self.log_action("LOGIN", f"Staff {username} signed in")
                return True
        print("Invalid username or password.")
        self.log_action("LOGIN_FAIL", f"Invalid staff login for {username}")
        return False
    
    def list_instruments(self):
        """
        Return the list of instruments.
        """
        os.system('cls')
        return self.instruments
    
    def list_students(self):
        """
        List all students with their details.
        """
        return [s.display_info() for s in self.students]
    
    def list_teachers(self):
        """
        Return a list of all teachers with their info.
        """
        os.system('cls')
        return [t.display_info() for t in self.teachers]
    
    def list_courses(self):
        """
        List all courses with their details.
        """
        os.system('cls')
        return [f"ID: {c.id} Name: {c.name} Instrument: {c.instrument}" for c in self.courses]
    
    def list_admins(self):
        """
        Return a list of all admins with ID and username.
        """
        os.system('cls')
        return [f"ID: {a.id} Username: {a.username}" for a in self.admin]
    
    def list_staff(self):
        """
        Return a list of all staff members with ID, name.
        """
        os.system('cls')
        return [f"ID: {s.id} Name: {s.name}" for s in self.staff]
    
    
    def add_lesson_to_course(self, course_id, title, day, time, duration_minutes):
        """
        Add a lesson to a course identified by course_id.
        """
        course = self.find_course_by_id(course_id)
        if not course:
            print("Error: Invalid course ID.")
            
            return False
        course.add_lesson(title, day, time, duration_minutes)
        self._save_data()
        print(f"Lesson '{title}' added to course '{course.name}'.")
        self.log_action("ADD_LESSON", f"Lesson added to {course.name}: {duration_minutes} min")
        return True

    def remove_student(self, student_id):
        """
        Remove a student and unenroll them from any courses.
        """
        student = self.find_student_by_id(student_id)
        if not student:
            print("Error: Invalid student ID.")
            
            return False
        self.log_action("REMOVE_STUDENT", f"Removed student: {student.name}")
        self.students.remove(student)
        # Remove student from enrolled lists in courses
        for course in self.courses:
            if student_id in course.enrolled_student_ids:
                course.enrolled_student_ids.remove(student_id)
        self._save_data()
        print(f"Removed student: {student.display_info()}")
        return True
    
    def remove_teacher(self, teacher_id):
        """
        Remove a teacher, all their courses, and unenroll students from those courses.
        """
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            print("Error: Invalid teacher ID.")
            
            return False

        # Find courses taught by teacher
        teacher_courses = [c for c in self.courses if c.teacher_id == teacher_id]
        teacher_course_ids = {c.id for c in teacher_courses}

        # Unenroll students from these courses
        for student in self.students:
            original_courses = set(student.enrolled_course_ids)
            updated_courses = original_courses - teacher_course_ids
            if original_courses != updated_courses:
                student.enrolled_course_ids = list(updated_courses)

        # Remove courses and teacher
        self.courses = [c for c in self.courses if c.teacher_id != teacher_id]
        self.log_action("REMOVE_TEACHER", f"Removed teacher: {teacher.name}")
        self.teachers.remove(teacher)

        self._save_data()
        print(f"Removed teacher: {teacher.display_info()} and their courses.")
        return True
    
    def remove_instrument(self, instrument_name):   
        """
        Remove an instrument by name.
        """
        if instrument_name not in self.instruments:
            print(f"Error: Instrument '{instrument_name}' not found.")
            return False
        self.instruments.remove(instrument_name)
        self.log_action("REMOVE_INSTRUMENT", f"Removed instrument: {instrument_name}")
        self._save_data()
        print(f"Removed instrument: {instrument_name}")
        return True
    
    def remove_admin(self, admin_id):
        """
        Remove an admin by ID.
        """
        admin = self.find_admin_by_id(admin_id)
        if not admin:
            print("Error: Invalid admin ID.")
            return False
        self.admin.remove(admin)
        self.log_action("REMOVE_ADMIN", f"Removed admin: {admin.username}")
        self._save_data()
        return True
    
    def remove_staff(self, staff_id):
        """
        Remove a staff member by ID.
        """
        staff = self.find_staff_by_id(staff_id)
        if not staff:
            print("Error: Invalid staff ID.")
            return False
        self.log_action("REMOVE_STAFF", f"Removed staff: {staff.name}")
        self.staff.remove(staff)
        self._save_data()
        print(f"Removed staff: ID: {staff.id} Name: {staff.name}")
        return True
    
    def remove_course(self, course_id):
        """
        Remove a course and unenroll students from it.
        """
        course = self.find_course_by_id(course_id)
        if not course:
            print("Error: Invalid course ID.")
            
            return False
        self.log_action("REMOVE_COURSE", f"Removed course: {course.name}")
        self.courses.remove(course)
        for student in self.students:
            if course_id in student.enrolled_course_ids:
                student.enrolled_course_ids.remove(course_id)
        self._save_data()
        print(f"Removed course: ID: {course.id} Name: {course.name} Instrument: {course.instrument}")
        
        return True

    def remove_lesson_from_course(self, course_id, lesson_title):
        """
        Remove a lesson by title from a specific course.
        """
        course = self.find_course_by_id(course_id)
        if not course:
            print("Error: Invalid course ID.")
            
            return False
        lesson_to_remove = next((l for l in course.lessons if l["title"] == lesson_title), None)
        if not lesson_to_remove:
            print(f"Error: Lesson '{lesson_title}' not found in course '{course.name}'.")
            
            return False
        course.lessons.remove(lesson_to_remove)
        self._save_data()
        print(f"Removed lesson '{lesson_title}' from course '{course.name}'.")
        
        return True

    def print_student_card(self, student_id):
        """
        Generate a text file as a student ID badge.
        """
        try:
            student_id = int(student_id)
        except ValueError:
            print("Error: Student ID must be an integer.")
            
            return

        student = self.find_student_by_id(student_id)

        if student:
            filename = f"{student_id}_card.txt"
            with open(filename, 'w') as f:
                f.write("========================\n")
                f.write("  MUSIC SCHOOL ID BADGE\n")
                f.write("========================\n")
                f.write(f"ID: {student.id}\n")
                f.write(f"Name: {student.name}\n")
                enrolled_courses = student.enrolled_course_ids if student.enrolled_course_ids else []
                courses_str = ', '.join(map(str, enrolled_courses)) if enrolled_courses else 'No courses enrolled'
                f.write(f"Enrolled In: {courses_str}\n")
                f.write("========================\n")

            print(f"Student card for {student.name} saved as {filename}.")
            
        else:
            print(f"Error: Student with ID {student_id} not found.")

    def edit_student(self, student_id, name=None):
        """
        Edit a student's name.
        """
        student = self.find_student_by_id(student_id)
        if not student:
            print("Error: Student not found.")
            
            return False
        if name:
            student.name = name
        self._save_data()
        print(f"Student {student_id} updated.")
        self.log_action("EDIT_STUDENT", f"Renamed student {student} → {name}")
        return True

    def edit_teacher(self, teacher_id, name=None, speciality=None):
        """
        Edit teacher's name and/or speciality.
        """
        teacher = self.find_teacher_by_id(teacher_id)
        if not teacher:
            print("Error: Teacher not found.")
            
            return False
        if name:
            teacher.name = name
        if speciality:
            teacher.speciality = speciality
        self._save_data()
        print(f"Teacher {teacher_id} updated.")
        self.log_action("EDIT_TEACHER", f"Edited teacher {teacher} → {name}, Specialty: {speciality}")
        return True

    def edit_admin(self, admin_id, username=None, password=None):
        """
        Edit admin's username and/or password.
        """
        admin = self.find_admin_by_id(admin_id)
        if not admin:
            print("Error: Admin not found.")
            
            return False
        if username:
            admin.username = username
        if password:
            admin.password = password
        self._save_data()
        print(f"Admin {admin_id} updated.")
        self.log_action("EDIT_ADMIN", f"Renamed admin {admin} → {username}")
        return True

    def edit_staff(self, staff_id, name=None, new_password=None):
        """
        Edit staff member's name and/or password.
        """
        staff = self.find_staff_by_id(staff_id)
        if not staff:
            print("Error: Staff not found.")
            
            return False
        if name:
            staff.name = name
        if new_password:
            staff.password = new_password
        self._save_data()
        print(f"Staff {staff_id} updated.")
        self.log_action("EDIT_STAFF", f"Renamed staff {staff} → {name}")
        return True

    def edit_instrument(self, old_name, new_name):
        """
        Rename an instrument and update courses that use it.
        """
        if old_name not in self.instruments:
            print(f"Error: Instrument '{old_name}' not found.")
            
            return False
        if new_name in self.instruments:
            print(f"Error: Instrument '{new_name}' already exists.")
            
            return False
        idx = self.instruments.index(old_name)
        self.instruments[idx] = new_name

        for course in self.courses:
            if course.instrument == old_name:
                course.instrument = new_name

        self._save_data()
        print(f"Instrument '{old_name}' renamed to '{new_name}'.")
        self.log_action("EDIT_INSTRUMENT", f"Renamed {old_name} → {new_name}")
        return True

    def front_desk_daily_roster(self, day):
        """
        Generate a simplified daily roster for front desk staff.
        """
        os.system('cls')
        if not isinstance(day, str):
            print("Error: Day must be a string.")
            
            return []

        valid_days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day = day.lower().strip()

        if day not in valid_days:
            print("Invalid day name.")
            
            return []

        roster = []
        for course in self.courses:
            for lesson in course.lessons:
                if lesson["day"].lower() == day:
                    teacher = self.find_teacher_by_id(course.teacher_id)
                    teacher_name = getattr(teacher, 'name', 'Unknown') if teacher else 'Unknown'
                    roster.append({
                        "course_name": course.name,
                        "teacher_name": teacher_name,
                        "lesson_title": lesson["title"],
                        "time": lesson["time"],
                        "duration": lesson["duration"],
                        "students_enrolled": len(course.enrolled_student_ids)
                    })
        return roster
    
    def get_enrolled_courses_for_student(self, student_id):
        """
        Return a list of Course objects that the given student is enrolled in.
        """
        student = self.find_student_by_id(student_id)
        if not student:
            print("Error: Student not found.")
            return []
        return [self.find_course_by_id(cid) for cid in student.enrolled_course_ids if self.find_course_by_id(cid)]

    
    def record_payment(self, student_id, amount, method):
        """
        Record a payment made by a student.
        Rejects invalid student IDs or non-positive amounts.
        """
        student = self.find_student_by_id(student_id)
        if not student:
            print("Error: Invalid student ID.")
            return False

        # Validate amount
        try:
            amount = float(amount)
        except ValueError:
            print("Error: Amount must be numeric.")
            return False

        if amount <= 0:
            print("Error: Payment amount must be greater than 0.")
            return False

        timestamp = datetime.datetime.now().isoformat()
        payment = {
            "student_id": student_id,
            "student_name": student.name,
            "amount": amount,
            "method": method,
            "timestamp": timestamp
        }

        self.finance_log.append(payment)
        self._save_data()
        self.log_action("PAYMENT", f"{student.name} paid RM{amount:.2f} via {method}")
        print(f"Payment recorded: {student.name} paid {amount:.2f} via {method} at {timestamp}.")
        return True



    def get_payment_history(self, student_id):
        """
        Return a list of payment records for a specific student.
        """
        student = self.find_student_by_id(student_id)
        if not student:
            print("Error: Invalid student ID.")
            return []

        history = [p for p in self.finance_log if p["student_id"] == student_id]
        return history


    def export_report(self, kind, out_path):
        """
        Export a JSON or CSV report for either 'payments' or 'attendance'.
        kind: 'payments' or 'attendance'
        out_path: file path to save the report
        """
        if kind not in ["payments", "attendance"]:
            print("Error: Invalid report type. Use 'payments' or 'attendance'.")
            return False

        data = self.finance_log if kind == "payments" else self.attendance_log

        # Determine export format
        if out_path.endswith(".json"):
            with open(out_path, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"{kind.title()} report exported to {out_path}")
            return True

        elif out_path.endswith(".csv"):
            if not data:
                print(f"No {kind} data to export.")
                return False

            keys = data[0].keys()
            with open(out_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            print(f"{kind.title()} report exported to {out_path}")
            self.log_action("EXPORT", f"{kind.capitalize()} report exported to {out_path}")
            return True

        else:
            print("Error: Unsupported file format. Use .json or .csv")
            return False
    


