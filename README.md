**This is the project repository for my portfolio website.**

It features a dashboard I created for the earthquakes near Turkey and my other projects. The challenge was to gain experience with web development and deployment while actively handling the reliability and security of the website using free services.

The website is built using Django, and deployed on a free-tier AWS EC2 instance. Total amount spent for the project is $1.16, only for the domain name.

***The website is accessible at:***

www.berkaybgk.site 



## Building the Project

In order to run the project on your local machine, you need to have Python and pip installed.

```bash
# Clone the repository
git clone https://github.com/berkaybgk/portfolio.git

# Change the directory
cd portfolio

# Install the requirements
pip install -r requirements.txt

# Create a django secret key
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Create a .env file in the root directory and add the following lines
SECRET_KEY=your_secret_key

# makemigrations and migrate
python manage.py makemigrations
python manage.py migrate

# Run the server, collect static files
python manage.py collectstatic --clear --noinput & python manage.py runserver

# Open your browser and go to http://127.0.0.1:8000/
```

