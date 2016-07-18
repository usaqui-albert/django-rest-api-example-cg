# Connect Good Backend

### Installation: ###

Run the following commands to install some dependencies and virtualenv:

     sudo apt-get install python-pip python-dev build-essential
     sudo pip install virtualenv

Clonning the project by ssh:

    git clone git@bitbucket.org:blanclink/connect-good-be-api.git

Before get into project folder you just cloned you must create the virtual environment typing the following:

    virtualenv env

This command is going to create an environment called "env", to activate it run:

    source env/bin/activate

After this you can get into the project folder.

    cd connect-good-be-api/

Remember to change to the right branch, then install the dependencies of the project:

    pip install -r requirements.txt

### Running ###

    python manage.py runserver <port_number>

If there is no port_number provided it will take port 8000 by default.

### Migrations ###

To run migrations to the database you have to type the following command:

    python manage.py migrate

### Running seeders(fixtures) ###

Type the following commands by the order than they appear:

    python manage.py loaddata countries/fixtures/countries.json
    python manage.py loaddata cities/fixtures/cities.json
    python manage.py loaddata users/fixtures/users.json
    python manage.py loaddata miscellaneous/fixtures/tax_receipts.json
    python manage.py loaddata miscellaneous/fixtures/customers.json
    python manage.py loaddata charities/fixtures/charities_by_category.json
    python manage.py loaddata charities/fixtures/charities_by_country.json

### Running Celery ###

    celery -A ConnectGood worker -l info