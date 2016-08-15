#!/bin/bash

python manage.py loaddata countries/fixtures/countries.json
python manage.py loaddata states/fixtures/states.json
python manage.py loaddata users/fixtures/users.json
python manage.py loaddata miscellaneous/fixtures/customers.json
python manage.py loaddata charities/fixtures/charities_by_category.json
python manage.py loaddata charities/fixtures/charities_by_country.json
