# NOTES ON USAGE:

```
flask db migrate
```

Run this command if your current changes alter any table schema.

```
flask db upgrade
```

Run this command to get the current up-to-date database schema.

# DATABASE ASSUMPTION:

Enrollment History is handled outside the database (through exporting) when the current semester ends and the Enrollment table is emptied before the new one begins.