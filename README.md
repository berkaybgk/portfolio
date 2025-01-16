This is the project repository for my portfolio website.

It features my data science projects, and the challenge was to gain experience with web development and deployment.

***The website is accessible at:***

www.berkaybgk.site 



## Building the Project

In order to run the project on your local machine, you need to have Python and pip installed.

1. Clone the repository to your local machine:

```bash
git clone https://github.com/berkaybgk/portfolio.git
```

2. Install the required libraries:

```bash
pip install -r requirements.txt
```

3. Generate a new secret key for the Django project:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

4. Create a `.env` file in the root directory of the project and add the following line:

```bash
SECRET_KEY= <your_secret_key>
```

5. Run the Django migrations:

```bash
python manage.py migrate
```

6. Create a superuser:

```bash
python manage.py createsuperuser
```

7. Run the Django development server:

```bash
python manage.py runserver
```

8. Access the website at `http://127.0.0.1:8000/`

