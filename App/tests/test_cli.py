import pytest
from click.testing import CliRunner
from wsgi import app
import uuid

@pytest.fixture
def runner():
    yield app.test_cli_runner()

def test_full_cli_workflow(runner):
    # Ensure tables exist in the CLI context
    runner.invoke(app.cli, ['init-db'])

    test_username = f"testuser_{uuid.uuid4().hex[:8]}"
    admin_username = f"testadmin_{uuid.uuid4().hex[:8]}"

    # 1. Create user
    result = runner.invoke(app.cli, ['user', 'create', test_username, 'testpass', 'admin'])
    print('Create user:', result.output)
    assert 'created' in result.output or result.exit_code == 0

    # 2. Create admin
    result = runner.invoke(app.cli, ['admin', 'create', admin_username, 'testadminpass'])
    print('Create admin:', result.output)
    assert 'created' in result.output or result.exit_code == 0

    # 3. List user
    result = runner.invoke(app.cli, ['user', 'list'])
    print('List user:', result.output)
    assert 'testuser' in result.output or result.exit_code == 0

    # 4. Get preferences
    result = runner.invoke(app.cli, ['user', 'get-preferences', '1'])
    print('Get preferences:', result.output)
    assert result.exit_code == 0

    # 4b. Update user preferences
    result = runner.invoke(app.cli, ['user', 'update-preferences', '1', '--abs_threshold', '10', '--perc_threshold', '0.2'])
    print('Update user preferences:', result.output)
    assert result.exit_code == 0

    # 5. Import venues
    result = runner.invoke(app.cli, ['admin', 'import-venues'])
    print('Import venues:', result.output)
    assert result.exit_code == 0

    # 6. Import students
    result = runner.invoke(app.cli, ['admin', 'import-students'])
    print('Import students:', result.output)
    assert result.exit_code == 0

    # 7. Import courses
    result = runner.invoke(app.cli, ['admin', 'import-courses'])
    print('Import courses:', result.output)
    assert result.exit_code == 0

    # 8. Import past timetable
    result = runner.invoke(app.cli, ['admin', 'import-past-timetable'])
    print('Import past timetable:', result.output)
    assert result.exit_code == 0

    # 9. Import enrollments
    result = runner.invoke(app.cli, ['admin', 'import-enrollments'])
    print('Import enrollments:', result.output)
    assert result.exit_code == 0

    # 10. Create clash matrix
    result = runner.invoke(app.cli, ['create-clash-matrix'])
    print('Create clash matrix:', result.output)
    assert result.exit_code == 0

    # 11. View venues
    result = runner.invoke(app.cli, ['admin', 'view-venues'])
    print('View venues:', result.output)
    assert result.exit_code == 0

    # 12. View venue
    result = runner.invoke(app.cli, ['admin', 'view-venue', 'JFK Auditorium'])
    print('View venue:', result.output)
    assert result.exit_code == 0

    # 13. View courses
    result = runner.invoke(app.cli, ['admin', 'view-courses'])
    print('View courses:', result.output)
    assert result.exit_code == 0

    # 14. View course
    result = runner.invoke(app.cli, ['admin', 'view-course', 'FOUN1105'])
    print('View course:', result.output)
    assert result.exit_code == 0

    # 15. View courses by subject
    result = runner.invoke(app.cli, ['admin', 'view-courses-by-subject', 'FOUN'])
    print('View courses by subject:', result.output)
    assert result.exit_code == 0

    # 16. View subject codes
    result = runner.invoke(app.cli, ['admin', 'view-subject-codes'])
    print('View subject codes:', result.output)
    assert result.exit_code == 0

    # 17. Course exists
    result = runner.invoke(app.cli, ['admin', 'course-exists', 'FOUN1105'])
    print('Course exists:', result.output)
    assert result.exit_code == 0

    # 18. View conflicting courses
    result = runner.invoke(app.cli, ['admin', 'view-conflicting-courses', '5', '0.1'])
    print('View conflicting courses:', result.output)
    assert result.exit_code == 0

    # 19. View course clashes
    result = runner.invoke(app.cli, ['admin', 'view-course-clashes', 'FOUN1105', '5', '0.1'])
    print('View course clashes:', result.output)
    assert result.exit_code == 0

    # 20. Get all exams
    result = runner.invoke(app.cli, ['admin', 'get-all-exams'])
    print('Get all exams:', result.output)
    assert result.exit_code == 0

    # 21. Get exams by date
    result = runner.invoke(app.cli, ['admin', 'get-exams-by-date', '2026-11-12'])
    print('Get exams by date:', result.output)
    assert result.exit_code == 0

    # 22. Reschedule exam by time
    result = runner.invoke(app.cli, ['admin', 'reschedule-exam', '1', '--time', '1'])
    print('Reschedule exam by time:', result.output)
    assert result.exit_code == 0

    # 23. Reschedule exam by venue
    result = runner.invoke(app.cli, ['admin', 'reschedule-exam', '1', '--venue_id', '1'])
    print('Reschedule exam by venue:', result.output)
    assert result.exit_code == 0

    # 24. Reschedule exam by date
    result = runner.invoke(app.cli, ['admin', 'reschedule-exam', '1', '--date', '2026-11-12'])
    print('Reschedule exam by date:', result.output)
    assert result.exit_code == 0

    # 25. Get exams that need rescheduling
    result = runner.invoke(app.cli, ['admin', 'get-exams-need-rescheduling'])
    print('Get exams that need rescheduling:', result.output)
    assert result.exit_code == 0

    # 26. Get all days with exams
    result = runner.invoke(app.cli, ['admin', 'get-all-days-with-exams'])
    print('Get all days with exams:', result.output)
    assert result.exit_code == 0

    # 27. Split exam 
    splits_json = '[{"number_of_students":10},{"number_of_students":10}]'
    # Omit --exam_id to test dynamic lookup (should work if BIOL1262 and venue exist) this is done for automated testing purposes
    result = runner.invoke(app.cli, ['admin', 'split-exam', splits_json, '--date', '2026-12-03', '--time', '4'])
    print('Split exam:', result.output)
    assert result.exit_code == 0

    # 28. Merge exams 
    result = runner.invoke(app.cli, [
        'admin', 'merge-exams',
        '--course_code', 'BIOL1262',
        '--date', '2026-12-03',
        '--time', '4',
        '--venue_id', '142'
    ])
    print('Merge exams:', result.output)
    assert result.exit_code == 0
