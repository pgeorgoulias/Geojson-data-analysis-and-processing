# Supporting software for maritime logistics and transportation
COP

Step 1: Open the command prompt and set the current directory to the one that the project 
	stored.

Step 2: Create a new virtual environment: virtualenv venv

Step 3: activate it using the command: source venv/Scripts/activate

Step 4: Check python version using the command: python --version

Step 5: Install the requirements by using the command: pip install -r requirements.txt

Step 6: Initialise the database with the following: python manage.py makemigrations

Step 7: Execute the migration with the following: python manage.py migrate

Step 8: Get the static files: python manage.py collectstatic

Step 9(optional): create a super user: winpty python manage.py createsuperuser

Step 10: run the server locally: python manage.py runserver

	The port will most likely be 127.0.0.1:8000, which you will input to your browser 
	once the server has started successfully.

NOTE: the project was created and developed using the anaconda environment and packages were install using the anaconda prompt.

Moreover, the dependencies can be found in the relevant file ('requirements.txt')

The current readme file can be found in the corpus documents and in the project repository.

Reference for the above information:
https://techsolutionshere.com/how-to-setup-and-run-an-existing-django-project-on-windows/
