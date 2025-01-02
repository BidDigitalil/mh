# Treatment Center Management System

## Project Overview
A Django-based management system for tracking and managing treatment center operations.

## Prerequisites
- Python 3.8.10
- Django 4.2.9
- Virtual Environment: `venv_3.8.10`

## Setup Instructions
1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv venv_3.8.10
   ```
3. Activate the virtual environment:
   - Windows: `venv_3.8.10\Scripts\activate`
   - Linux/Mac: `source venv_3.8.10/bin/activate`
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Start the development server:
   ```
   python manage.py runserver 4444
   ```

## Key Dependencies
- Django 4.2.9
- django-crispy-forms 2.0
- django-filter 23.3
- djangorestframework 3.13.1

## Notes
- Ensure you are using Python 3.8.10
- This project uses a custom virtual environment setup

## Project Structure
- `treatment_app/`: Main application directory
- `treatment_center/`: Project configuration
- `manage.py`: Django management script
- `requirements.txt`: Project dependencies

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[Specify your license here]

## Contact
[Your contact information]
