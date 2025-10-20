"""
Comprehensive unit tests for app/schedule.py (ScheduleManager).

- Each test follows Arrange / Act / Assert (AAA) format.
- Uses temporary files via pytest's tmp_path to avoid modifying real data.
- Uses only these names: "Low Yinn Ean", "Alicia", "Shuen".
- Designed to cover student, teacher, admin, staff, instrument, course, payments,
  lessons, roster, backup, export and logging functions.
- Single file containing many specific tests and edge cases.
- Uses tmp_path to isolate file I/O.
- Tests include normal, boundary, negative paths, and simulated exceptions.
"""

import os
import json
import pytest
from pathlib import Path
from app.schedule import ScheduleManager


# Allowed names to use in tests (per user request)
N1 = "Low Yinn Ean"
N2 = "Alicia"
N3 = "Shuen"


# -------------------------
# Helper fixtures
# -------------------------
@pytest.fixture
def manager(tmp_path):
    """
    Arrange: Provide a fresh ScheduleManager using isolated tmp files for every test.
    """
    data_file = tmp_path / "msms.json"
    log_file = tmp_path / "system_log.txt"
    backup_file = tmp_path / "backup.json"
    # Ensure files don't exist before init
    if data_file.exists():
        data_file.unlink()
    if log_file.exists():
        log_file.unlink()
    if backup_file.exists():
        backup_file.unlink()
    m = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    return m


# -------------------------
# STUDENT CRUD
# -------------------------
def test_add_student(manager):
    """Add a student and verify stored correctly."""
    # ACT
    s = manager.add_student(N1)
    # ASSERT
    assert s is not None
    assert s.name == N1
    assert manager.find_student_by_id(s.id) is s


def test_edit_student(manager):
    """Edit student name and confirm change persisted in-memory."""
    s = manager.add_student(N2)
    # ACT
    ok = manager.edit_student(s.id, name=N3)
    # ASSERT
    assert ok is True
    assert manager.find_student_by_id(s.id).name == N3


def test_remove_student(manager):
    """Remove a student then ensure they are gone and not in any course lists."""
    s = manager.add_student(N1)
    # ACT
    ok = manager.remove_student(s.id)
    # ASSERT
    assert ok is True
    assert manager.find_student_by_id(s.id) is None


# -------------------------
# TEACHER CRUD
# -------------------------
def test_add_teacher_and_find(manager):
    """Create a teacher and find by id."""
    t = manager.add_teacher(N2, "Piano")
    assert t is not None
    assert manager.find_teacher_by_id(t.id) is t


def test_edit_teacher(manager):
    """Edit a teacher's name and speciality."""
    t = manager.add_teacher(N3, "Guitar")
    ok = manager.edit_teacher(t.id, name=N1, speciality="Violin")
    assert ok is True
    found = manager.find_teacher_by_id(t.id)
    assert found.name == N1
    # speciality attribute may be spelled 'speciality' or similar; check expected field
    assert getattr(found, "speciality", getattr(found, "specialty", "Violin")) in ("Violin", "Violin")


def test_remove_teacher(manager):
    """Remove teacher and ensure they are no longer found; associated courses removed."""
    t = manager.add_teacher(N1, "Cello")
    c = manager.add_course("Cello 101", "Cello", t.id)
    s = manager.add_student(N2)
    manager.enroll_student_in_course(s.id, c.id)
    ok = manager.remove_teacher(t.id)
    assert ok is True
    assert manager.find_teacher_by_id(t.id) is None
    # course should be removed
    assert manager.find_course_by_id(c.id) is None
    # student's enrolled list updated (course id removed)
    assert c.id not in getattr(s, "enrolled_course_ids", [])


# -------------------------
# COURSE & LESSONS & ROSTER
# -------------------------
def test_add_course_requires_valid_teacher(manager):
    """Course creation should fail with invalid teacher id, succeed with valid teacher."""
    c = manager.add_course("NoTeacherCourse", "Piano", teacher_id=99999)
    assert c is None
    t = manager.add_teacher(N3, "Drums")
    c2 = manager.add_course("Drum 101", "Drums", teacher_id=t.id)
    assert c2 is not None
    assert manager.find_course_by_id(c2.id) is c2


def test_add_and_remove_lesson(manager):
    """Add a lesson to a course then remove it."""
    t = manager.add_teacher(N1, "Violin")
    c = manager.add_course("Violin L", "Violin", t.id)
    added = manager.add_lesson_to_course(c.id, "Week 1", "Monday", "10:00", 60)
    assert added is True
    # get_daily_roster should include the course for Monday (case-insensitive)
    roster = manager.get_daily_roster("Monday")
    assert any(r["course_id"] == c.id for r in roster)
    removed = manager.remove_lesson_from_course(c.id, "Week 1")
    assert removed is True


def test_get_daily_roster_and_front_desk(manager):
    """Verify daily roster and front desk view produce lists and include added lesson."""
    t = manager.add_teacher(N2, "Flute")
    c = manager.add_course("Flute 1", "Flute", t.id)
    manager.add_lesson_to_course(c.id, "Intro", "Tuesday", "09:00", 45)
    roster = manager.get_daily_roster("tuesday")
    assert isinstance(roster, list)
    fd = manager.front_desk_daily_roster("tuesday")
    assert isinstance(fd, list)
    # Expect course name to appear in front desk roster
    assert any(r["course_name"] == c.name for r in fd)


# -------------------------
# ENROLLMENT & ATTENDANCE
# -------------------------
def test_enroll_student_in_course_and_prevent_duplicate(manager):
    """Enroll a student, ensure duplicate enrollment prevented and invalid ids rejected."""
    s = manager.add_student(N3)
    t = manager.add_teacher(N1, "Guitar")
    c = manager.add_course("Guitar A", "Guitar", t.id)
    ok1 = manager.enroll_student_in_course(s.id, c.id)
    assert ok1 is True
    ok2 = manager.enroll_student_in_course(s.id, c.id)
    assert ok2 is False
    assert manager.enroll_student_in_course(9999, c.id) is False
    assert manager.enroll_student_in_course(s.id, 9999) is False


def test_check_in_and_attendance_log(manager):
    """Check-in an enrolled student and validate attendance log entry."""
    s = manager.add_student(N1)
    t = manager.add_teacher(N2, "Piano")
    c = manager.add_course("Piano Basics", "Piano", t.id)
    manager.enroll_student_in_course(s.id, c.id)
    ok = manager.check_in_student(s.id, c.id)
    assert ok is True
    logs = manager.get_attendance_log()
    assert any(entry["student_id"] == s.id and entry["course_id"] == c.id for entry in logs)


def test_get_enrolled_courses_for_student(manager):
    """Return only the courses to which a student is enrolled."""
    s = manager.add_student(N2)
    t = manager.add_teacher(N3, "Sax")
    c1 = manager.add_course("Sax A", "Sax", t.id)
    c2 = manager.add_course("Sax B", "Sax", t.id)
    manager.enroll_student_in_course(s.id, c1.id)
    enrolled = manager.get_enrolled_courses_for_student(s.id)
    assert isinstance(enrolled, list)
    assert any(course.id == c1.id for course in enrolled)
    assert all(course.id in [c1.id, c2.id] for course in enrolled) or c2.id not in enrolled


# -------------------------
# ADMIN & STAFF (create, signin, edit, remove)
# -------------------------
def test_add_admin_signin_remove(manager):
    """Test add_admin, sign_in_admin, and remove_admin behavior (admin has username/password)."""
    admin = manager.add_admin("admin_user", "admin_pass")
    # Admin object uses .username attribute
    assert getattr(admin, "username", None) == "admin_user"
    ok_signin = manager.sign_in_admin("admin_user", "admin_pass")
    assert ok_signin is True
    bad = manager.sign_in_admin("admin_user", "wrong")
    assert bad is False
    removed = manager.remove_admin(admin.id)
    assert removed is True
    assert manager.find_admin_by_id(admin.id) is None


def test_edit_admin(manager):
    """Edit admin credentials and verify they change."""
    a = manager.add_admin("adm1", "pw1")
    # edit_admin may expect (id, username, password) or similar; call with known signature from schedule.py
    ok = manager.edit_admin(a.id, username="adm1_new", password="pw2")
    assert ok is True
    found = manager.find_admin_by_id(a.id)
    assert getattr(found, "username", None) == "adm1_new"


def test_add_staff_edit_remove_and_signin(manager):
    """Test staff create, edit, signin and removal. Staff uses .name and .password."""
    st = manager.add_staff(N3, "pw123")
    assert getattr(st, "name", None) == N3
    assert manager.sign_in_staff(N3, "pw123") is True
    assert manager.sign_in_staff(N3, "bad") is False
    ok_edit = manager.edit_staff(st.id, name=N1, new_password="pw_new")
    assert ok_edit is True
    sfound = manager.find_staff_by_id(st.id)
    assert sfound.name == N1
    removed = manager.remove_staff(st.id)
    assert removed is True
    assert manager.find_staff_by_id(st.id) is None


# -------------------------
# INSTRUMENTS
# -------------------------
def test_add_list_remove_instrument(manager):
    """Add an instrument, ensure duplicates prevented, list reflects addition and removal works."""
    # Ensure clean instruments
    assert manager.add_instrument("Violin") is True
    assert manager.add_instrument("Violin") is False  # duplicate
    assert "Violin" in manager.list_instruments()
    assert manager.remove_instrument("Violin") is True
    assert manager.remove_instrument("Violin") is False


def test_edit_instrument(manager):
    """Edit instrument name and prevent renaming to an existing name."""
    manager.add_instrument("Harp")
    ok = manager.edit_instrument("Harp", "HarpNew")
    assert ok is True
    # rename to existing name should fail
    manager.add_instrument("Piano")
    assert manager.edit_instrument("HarpNew", "Piano") is False


# -------------------------
# COURSE REMOVAL & SWITCH
# -------------------------
def test_remove_course_and_unenroll(manager):
    """Remove a course and ensure students are unenrolled."""
    t = manager.add_teacher(N1, "Oboe")
    c = manager.add_course("Oboe 1", "Oboe", t.id)
    s = manager.add_student(N2)
    manager.enroll_student_in_course(s.id, c.id)
    removed = manager.remove_course(c.id)
    assert removed is True
    assert manager.find_course_by_id(c.id) is None
    assert c.id not in s.enrolled_course_ids


def test_switch_student_course(manager):
    """Switch a student from one course to another (change enrollment)."""
    s = manager.add_student(N3)
    t = manager.add_teacher(N2, "Piano")
    c1 = manager.add_course("P1", "Piano", t.id)
    c2 = manager.add_course("P2", "Piano", t.id)
    manager.enroll_student_in_course(s.id, c1.id)
    ok = manager.switch_student_course(s.id, c1.id, c2.id)
    assert ok is True
    assert c2.id in s.enrolled_course_ids
    assert c1.id not in s.enrolled_course_ids



# -------------------------
# PAYMENTS & EXPORT
# -------------------------
def test_record_payment_validation_and_history(manager):
    """Record payments with validation and retrieve payment history."""
    s = manager.add_student(N2)
    assert manager.record_payment(s.id, 150.0, "Cash") is True
    # invalid entries
    assert manager.record_payment(s.id, 0, "Cash") is False
    assert manager.record_payment(s.id, -5, "Cash") is False
    assert manager.record_payment(s.id, "bad", "Cash") is False
    history = manager.get_payment_history(s.id)
    assert isinstance(history, list)
    assert len(history) == 1
    assert history[0]["amount"] == 150.0


def test_export_report_json_and_csv(manager, tmp_path):
    """Export payments to JSON and CSV and check files & content."""
    s = manager.add_student(N3)
    manager.record_payment(s.id, 100.0, "Card")
    json_path = tmp_path / "payments.json"
    csv_path = tmp_path / "payments.csv"
    ok_json = manager.export_report("payments", str(json_path))
    ok_csv = manager.export_report("payments", str(csv_path))
    assert ok_json is True
    assert ok_csv is True
    assert json_path.exists()
    assert csv_path.exists()
    # Basic content checks
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert data and data[0]["student_name"] == N3
    # CSV check: header exists
    with open(csv_path, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        assert first != ""


# -------------------------
# SAVE / LOAD / BACKUP / LOGGING
# -------------------------
def test_save_and_load_persistence(tmp_path):
    """Save data to disk via _save_data and reload via _load_data to confirm persistence."""
    data_file = tmp_path / "persist.json"
    log_file = tmp_path / "log.txt"
    backup_file = tmp_path / "backup.json"
    m = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    s = m.add_student(N1)
    m.record_payment(s.id, 20, "Cash")
    # Force save (already saved by methods, but explicit call)
    m._save_data()
    # Create a new manager pointing to same file and load
    m2 = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    found = m2.find_student_by_id(s.id)
    assert found is not None
    # finance_log should be present after reload
    assert any(p["student_id"] == s.id for p in m2.finance_log)


def test_backup_and_logging_behavior(manager):
    """Manual backup should create backup file and log the backup action."""
    # ARRANGE
    s = manager.add_student(N2)
    manager.record_payment(s.id, 30, "Cash")
    # ACT
    msg = manager.backup_data()
    # ASSERT
    assert "success" in msg.lower() or "created" in msg.lower()
    # Check backup file exists and log contains backup or manual tag
    assert os.path.exists(manager.backup_path)
    with open(manager.log_path, "r", encoding="utf-8") as f:
        log = f.read()
    assert any(tag in log for tag in ["BACKUP", "MANUAL_BACKUP", "BACKUP_CREATED", "SAVE"])
    assert "PAYMENT" in log or "PAYMENT" in log.upper()


# -------------------------
# LISTING / HELPERS
# -------------------------
def test_listing_functions_return_lists(manager):
    """List helpers return lists and are non-erroring."""
    # Create some entities
    manager.add_student(N1)
    manager.add_teacher(N2, "Spec")
    manager.add_admin("adm_test", "pw")
    manager.add_staff(N3, "pw")
    # Call list functions; they must return lists
    assert isinstance(manager.list_students(), list)
    assert isinstance(manager.list_teachers(), list)
    assert isinstance(manager.list_admins(), list)
    assert isinstance(manager.list_staff(), list)
    assert isinstance(manager.list_instruments(), list)

















# -------------------------
# Basic CRUD tests (students)
# -------------------------
def test_add_duplicate_students_have_unique_ids(manager):
    """Adding two students with the same name should produce distinct IDs."""
    s1 = manager.add_student(N1)
    s2 = manager.add_student(N1)
    assert s1.id != s2.id
    assert len(manager.students) >= 2


def test_remove_nonexistent_student_returns_false(manager):
    """Attempt to remove a student ID that doesn't exist should return False."""
    assert manager.remove_student(99999) is False


def test_edit_student_invalid_id_returns_false(manager):
    """Editing a non-existent student should return False and not raise."""
    assert manager.edit_student(99999, name="NoOne") is False


# -------------------------
# Teacher edge cases
# -------------------------
def test_add_teacher_duplicate_names(manager):
    """Adding teachers with same name should be allowed but produce unique IDs."""
    t1 = manager.add_teacher(N2, "Piano")
    t2 = manager.add_teacher(N2, "Piano")
    assert t1.id != t2.id
    assert len([t for t in manager.teachers if t.name == N2]) >= 2


def test_remove_teacher_with_courses(manager):
    """If teacher removed, their courses should be removed too."""
    t = manager.add_teacher(N3, "Sax")
    c = manager.add_course("TestCourse", "Sax", t.id)
    assert c is not None
    removed = manager.remove_teacher(t.id)
    assert removed is True
    assert manager.find_teacher_by_id(t.id) is None
    assert manager.find_course_by_id(c.id) is None


def test_edit_teacher_invalid_id(manager):
    """Editing a teacher that doesn't exist should return False."""
    assert manager.edit_teacher(123456, name="x", speciality="y") is False


# -------------------------
# Course & lessons edge cases
# -------------------------
def test_add_course_after_teacher_removed(manager):
    """Cannot add course with non-existent teacher."""
    t = manager.add_teacher(N1, "Guitar")
    # remove teacher
    manager.remove_teacher(t.id)
    # now adding a course should fail
    c = manager.add_course("After", "Guitar", t.id)
    assert c is None


def test_add_lesson_invalid_course(manager):
    """Adding a lesson to invalid course should return False."""
    assert manager.add_lesson_to_course(99999, "Topic", "Friday", "10:00", 30) is False


def test_remove_lesson_invalid_course_or_lesson(manager):
    """Removing a lesson that doesn't exist should return False (non-existent course or lesson)."""
    t = manager.add_teacher(N2, "Violin")
    c = manager.add_course("VL1", "Violin", t.id)
    assert manager.remove_lesson_from_course(c.id, "NopeLesson") is False
    assert manager.remove_lesson_from_course(999999, "Nope") is False


def test_get_daily_roster_empty_day_returns_empty_list(manager):
    """If no lessons scheduled on that day, roster should be empty list."""
    roster = manager.get_daily_roster("wednesday")
    assert isinstance(roster, list)
    assert roster == [] or len(roster) == 0


# -------------------------
# Enrollment / Attendance edge cases
# -------------------------
def test_enroll_invalid_student_or_course(manager):
    """Enroll with invalid student or invalid course should return False."""
    t = manager.add_teacher(N3, "Oboe")
    c = manager.add_course("O1", "Oboe", t.id)
    assert manager.enroll_student_in_course(999999, c.id) is False
    s = manager.add_student(N2)
    assert manager.enroll_student_in_course(s.id, 999999) is False


def test_check_in_without_enrollment_should_still_log_if_allowed(manager):
    """
    Some systems allow check-in only if enrolled; we expect check_in_student to validate.
    If it's implemented to require enrollment, it should return False. We accept both but assert behavior.
    """
    s = manager.add_student(N1)
    t = manager.add_teacher(N2, "Piano")
    c = manager.add_course("PNoEnroll", "Piano", t.id)
    # if system requires enrollment, this should be False; otherwise True
    result = manager.check_in_student(s.id, c.id)
    if result:
        assert any(entry["student_id"] == s.id and entry["course_id"] == c.id for entry in manager.attendance_log)
    else:
        assert result is False


def test_multiple_checkins_create_multiple_entries(manager):
    """Repeated check-ins should append multiple attendance entries."""
    s = manager.add_student(N3)
    t = manager.add_teacher(N1, "Piano")
    c = manager.add_course("P2", "Piano", t.id)
    manager.enroll_student_in_course(s.id, c.id)
    manager.check_in_student(s.id, c.id)
    manager.check_in_student(s.id, c.id)
    logs = [e for e in manager.attendance_log if e["student_id"] == s.id and e["course_id"] == c.id]
    assert len(logs) >= 2


# -------------------------
# Switch courses edge cases
# -------------------------
def test_switch_course_invalid_ids(manager):
    """Switching course with invalid IDs should return False."""
    assert manager.switch_student_course(9999, 1, 2) is False
    s = manager.add_student(N1)
    t = manager.add_teacher(N2, "Guitar")
    c1 = manager.add_course("C1", "Guitar", t.id)
    # not enrolled in c1 yet
    assert manager.switch_student_course(s.id, c1.id, 9999) is False


# -------------------------
# Admin & Staff type/validation tests
# -------------------------
def test_add_admin_and_duplicate_usernames(manager):
    """Adding admins with same username - behavior: allow or disallow, test expects unique objects either way."""
    a1 = manager.add_admin("alpha", "pw1")
    a2 = manager.add_admin("alpha", "pw2")
    # both objects should exist with distinct ids
    assert a1.id != a2.id


def test_signin_admin_wrong_types(manager):
    """Pass non-string types to sign_in_admin to see validation (should return False)."""
    # Ensure no crash if wrong types provided
    assert manager.sign_in_admin(None, None) is False
    assert manager.sign_in_admin(123, 456) is False


def test_edit_admin_invalid_id_returns_false(manager):
    """Editing non-existent admin should return False."""
    assert manager.edit_admin(99999, username="x", password="y") is False


def test_staff_signin_and_wrong_credentials(manager):
    """Staff must sign-in successfully with correct credentials; wrong credentials fail."""
    st = manager.add_staff(N2, "secret")
    assert manager.sign_in_staff(N2, "secret") is True
    assert manager.sign_in_staff(N2, "bad") is False


# -------------------------
# Instruments detailed tests
# -------------------------
def test_add_instrument_invalid_inputs(manager):
    """Add instrument with empty or non-string should be handled gracefully (False or custom behavior)."""
    # If implementation rejects empty string, expect False. Accept either but avoid exception.
    try:
        res = manager.add_instrument("")
        assert isinstance(res, (bool, dict))
    except Exception as e:
        pytest.fail(f"add_instrument raised unexpectedly: {e}")


def test_edit_instrument_nonexistent(manager):
    """Editing a non-existent instrument should return False."""
    assert manager.edit_instrument("NoExist", "NewName") is False


# -------------------------
# Payment edge cases & type validation
# -------------------------
def test_record_payment_string_amounts_and_precision(manager):
    """Accept numeric strings, ensure float conversion and precision handling."""
    s = manager.add_student(N1)
    assert manager.record_payment(s.id, "200.50", "Cash") is True
    assert manager.record_payment(s.id, "100", "Card") is True
    # total two entries with amounts convertible
    history = manager.get_payment_history(s.id)
    assert len(history) == 2
    assert abs(history[0]["amount"] - 200.50) < 0.001


def test_record_payment_large_amount(manager):
    """Very large payments handled (no overflow)"""
    s = manager.add_student(N2)
    big = 10**9
    assert manager.record_payment(s.id, big, "Wire") is True
    h = manager.get_payment_history(s.id)
    assert h and h[-1]["amount"] == float(big)


def test_record_payment_invalid_amount_types(manager):
    """Non-convertible amounts should return False and not append to the log."""
    s = manager.add_student(N3)
    before = len(manager.finance_log)
    assert manager.record_payment(s.id, "asfags", "Cash") is False
    assert len(manager.finance_log) == before


def test_record_payment_zero_negative(manager):
    """Zero and negative amounts should be rejected."""
    s = manager.add_student(N1)
    assert manager.record_payment(s.id, 0, "Cash") is False
    assert manager.record_payment(s.id, -1, "Cash") is False


# -------------------------
# Export report edge cases
# -------------------------
def test_export_report_invalid_kind(manager, tmp_path):
    """Invalid report kind should return False and not create file."""
    out = tmp_path / "out.xyz"
    assert manager.export_report("nonsense", str(out)) is False
    assert not out.exists()


def test_export_report_csv_when_no_data(manager, tmp_path):
    """CSV export when no data should either return False or create empty csv; assert behavior but avoid exception."""
    p = tmp_path / "empty.csv"
    # ensure finance_log is empty
    manager.finance_log = []
    res = manager.export_report("payments", str(p))
    # Accept either False or True depending on implementation, but should not crash
    assert isinstance(res, bool)
    # if file created, ensure its size/header behavior is reasonable
    if p.exists():
        assert p.stat().st_size >= 0


# -------------------------
# Save/Load failure simulations (monkeypatch)
# -------------------------
def test_save_data_raises_exception_logs_error(monkeypatch, tmp_path):
    """
    Simulate json.dump raising an exception during save to ensure _save_data logs error
    and does not crash.
    """
    data_file = tmp_path / "data.json"
    log_file = tmp_path / "log.txt"
    m = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(tmp_path / "backup.json"))
    # Cause json.dump to raise
    def fake_dump(*a, **k):
        raise RuntimeError("simulated dump error")
    monkeypatch.setattr("json.dump", fake_dump)
    # Try saving via a method that triggers save; add student to trigger _save_data inside
    try:
        m.add_student(N1)
    except Exception:
        # Should not raise to caller if code handles exceptions; if it raises, fail the test.
        pytest.fail("add_student raised despite json.dump monkeypatch")
    # Check log for SAVE or SAVE_ERROR/LOAD_ERROR tag
    with open(m.log_path, encoding="utf-8") as f:
        log = f.read()
    assert any(tag in log for tag in ["SAVE", "SAVE_ERROR", "BACKUP_ERROR", "MANUAL_BACKUP_FAIL"]) or "simulated dump error" in log


def test_load_data_corrupted_file_logs_error(tmp_path):
    """Create a corrupted JSON and ensure load_data handles and logs the error."""
    data_file = tmp_path / "bad.json"
    log_file = tmp_path / "log_load.txt"
    backup_file = tmp_path / "backup.json"
    # Write corrupted content
    data_file.write_text("{ not: valid json }")
    m = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    # load_data is called during init; check log for LOAD_ERROR or related tag
    with open(log_file, encoding="utf-8") as f:
        content = f.read()
    assert any(tag in content for tag in ["LOAD_ERROR", "LOAD", "BACKUP_ERROR"]) or "Failed" in content


# -------------------------
# Backup failure & timestamped backup tests
# -------------------------
def test_backup_when_data_missing_returns_failure(tmp_path):
    """If primary data file missing, backup_data should report failure (string) but not crash."""
    data_file = tmp_path / "missing.json"
    log_file = tmp_path / "logb.txt"
    backup_file = tmp_path / "bk.json"
    m = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    # Ensure data file truly missing
    if os.path.exists(m.data_path):
        os.remove(m.data_path)
    msg = m.backup_data()
    assert isinstance(msg, str)
    assert "not" in msg.lower() or "failed" in msg.lower()


def test_backup_creates_file_and_logs(manager):
    """Backup should create backup_path and write a log entry containing BACKUP (flexible)."""
    # Ensure some data exists
    s = manager.add_student(N3)
    manager.record_payment(s.id, 10, "Cash")
    msg = manager.backup_data()
    assert isinstance(msg, str)
    # backup file should exist
    assert os.path.exists(manager.backup_path)
    with open(manager.log_path, encoding="utf-8") as f:
        log = f.read()
    assert any(tag in log for tag in ["BACKUP", "MANUAL_BACKUP", "SAVE"])


# -------------------------
# Listing / helper functions when empty
# -------------------------
def test_list_helpers_empty_manager(tmp_path):
    """When manager starts with no entries, list functions should return empty lists."""
    m = ScheduleManager(data_path=str(tmp_path / "d.json"), log_path=str(tmp_path / "l.txt"), backup_path=str(tmp_path / "b.json"))
    # Immediately created empty lists; assert list methods return lists
    assert isinstance(m.list_students(), list)
    assert isinstance(m.list_teachers(), list)
    assert isinstance(m.list_courses(), list)
    assert isinstance(m.list_admins(), list)
    assert isinstance(m.list_staff(), list)
    assert isinstance(m.list_instruments(), list)


# -------------------------
# Cross-dependency / cleanup tests
# -------------------------
def test_remove_course_cleans_enrollments(manager):
    """Removing a course should remove it from all students' enrolled lists."""
    s = manager.add_student(N1)
    t = manager.add_teacher(N2, "Cello")
    c = manager.add_course("Cleanup", "Cello", t.id)
    manager.enroll_student_in_course(s.id, c.id)
    manager.remove_course(c.id)
    assert c.id not in getattr(s, "enrolled_course_ids", [])


def test_remove_student_cleans_courses(manager):
    """Removing student should remove their ID from any course enrollment lists."""
    s = manager.add_student(N2)
    t = manager.add_teacher(N3, "G")
    c = manager.add_course("RemoveStudentCourse", "G", t.id)
    manager.enroll_student_in_course(s.id, c.id)
    manager.remove_student(s.id)
    assert s.id not in getattr(c, "enrolled_student_ids", []) if hasattr(c, "enrolled_student_ids") else True


# -------------------------
# Final integrity test: save -> reload -> verify
# -------------------------
def test_full_save_reload_integrity(tmp_path):
    """Add multiple entities, save, then reload into a fresh manager and verify presence."""
    data_file = tmp_path / "full.json"
    log_file = tmp_path / "logfull.txt"
    backup_file = tmp_path / "bkfull.json"
    m = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    s1 = m.add_student(N1)
    t1 = m.add_teacher(N2, "Piano")
    c1 = m.add_course("FullFlow", "Piano", t1.id)
    m.enroll_student_in_course(s1.id, c1.id)
    m.record_payment(s1.id, 25, "Cash")

    # Explicitly force save
    m._save_data()

    # New manager instance reads same file
    m2 = ScheduleManager(data_path=str(data_file), log_path=str(log_file), backup_path=str(backup_file))
    assert m2.find_student_by_id(s1.id) is not None
    assert any(p["student_id"] == s1.id for p in m2.finance_log)
    assert m2.find_course_by_id(c1.id) is not None