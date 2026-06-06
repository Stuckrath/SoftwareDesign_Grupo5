reset-db:
	rm -f db.sqlite3
	rm -f mi_app/migrations/00*.py
	python manage.py makemigrations mi_app
	python manage.py migrate
	python manage.py loaddata datos_prueba.json
run:
	python manage.py runserver
admin:
	python manage.py createsuperuser