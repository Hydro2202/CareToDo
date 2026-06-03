# CareToDo

CareToDo is a Django-based nurse task management system designed to help healthcare staff manage patients, tasks, and schedules in a small clinical or hospital setting.

## What this system is all about

CareToDo provides a lightweight care coordination interface for nurses and medical staff. It centralizes patient records, task assignments, and progress tracking so staff can view and update:

- Patient details and medical notes
- Nurse assignments and departments
- Care tasks with scheduled date/time, status, and priority
- Task progress reports and completion status

The system supports user authentication, a dashboard experience, and both HTML views and API endpoints for common workflows.

## Key features

- Nurse list and patient management
- Task creation, editing, deletion, and completion tracking
- Dashboard summaries for pending, in-progress, and completed tasks
- Patient detail pages and reports overview
- User login/signup and profile support
- REST-style API endpoints for nurses, patients, tasks, and profiles

## Typical users

CareToDo is intended for nurses, care coordinators, and small care teams who need a simple web tool to:

- organize patient care assignments
- track care tasks by status
- manage daily nurse responsibilities
- review task completion reports

## Project structure

- `manage.py` — Django management utility
- `config/` — Django settings and URL configuration
- `tasks/` — main application with models, views, templates, URLs, and tests
- `templates/` — base templates and shared views
- `static/` — CSS and JavaScript support files

## Getting started

1. Create and activate a Python virtual environment.
2. Install dependencies from `requirements.txt`.
3. Run Django migrations.
4. Start the development server.

> Example commands:
> ```bash
> python -m venv venv
> venv\Scripts\activate
> pip install -r requirements.txt
> python manage.py migrate
> python manage.py runserver
> ```

## Notes

This project appears to focus on nurse-centered task and patient management rather than full electronic health record (EHR) functionality. It is best suited as a care coordination tool for a small team or pilot environment.
