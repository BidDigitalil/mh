# Treatment Center Management System

## Project Overview
This is a Django-based web application for managing a treatment center, providing functionalities for user management, family file tracking, and administrative operations.

## Prerequisites
- Python 3.8+
- Django 5.0
- Virtual Environment recommended

## Installation

1. Clone the repository
```bash
git clone [repository-url]
cd treatment_center
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up the database
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Run the development server
```bash
python manage.py runserver
```

## Key Dependencies
- Django: Web framework
- django-crispy-forms: Enhanced form rendering
- django-filter: Advanced filtering
- djangorestframework: API development
- reportlab: PDF generation
- Pillow: Image processing

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
