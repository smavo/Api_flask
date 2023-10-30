
https://flask.palletsprojects.com/en/3.0.x/
https://pypi.org/project/Flask/
pip install flask

https://flask-sqlalchemy.palletsprojects.com/en/2.x/quickstart/
https://pypi.org/project/Flask-SQLAlchemy/
pip install flask_sqlalchemy

# Ejecutar aplicacion
flask --app app --debug run

# Ejecutarlo asi cuando tiene flasenv configurado
flask run

https://flask-smorest.readthedocs.io/en/latest/
https://pypi.org/project/flask-smorest/
pip install flask-smorest

https://pypi.org/project/python-dotenv/
pip install python-dotenv

https://marshmallow.readthedocs.io/en/stable/
pip install -U marshmallow

https://flask-jwt-extended.readthedocs.io/en/stable/
https://pypi.org/project/Flask-JWT-Extended/
pip install Flask-JWT-Extended

https://pypi.org/project/passlib/
pip install passlib

https://flask-migrate.readthedocs.io/en/latest/
https://pypi.org/project/Flask-Migrate/
pip install Flask-Migrate


# Esto creará una migración dentro de la carpeta de su proyecto.
flask db init 

# Genera la migración
flask db migrate -m "Initial migration."

# Aplicar cambios de la migración
flask db upgrade

https://pypi.org/project/psycopg2/
pip install psycopg2