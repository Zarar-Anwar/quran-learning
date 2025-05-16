
### PYTHON
````shell
virtualenv env
env/Scripts/activate
source env/bin/activate
pip install -r requirements.txt
pip install package
pip uninstall package
pip freeze
````
### DJANGO
````shell
django-admin startproject projectname
django-admin startapp appname
python manage.py makemigrtions
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic
python manage.py runserver
````
### STRIPE
````shell
stripe login
stripe listen --forward-to 127.0.0.1:8000/url/webhook/
````
### GIT
````shell
git init
git remote add origin github_repository
git config --global user.name github_username
git config --global user.email github_email
git clone github_repository
git status
git log
git branch
git checkout -b branch_name
git add .
git commit -m "commit_message"
git push
````

### ENDPOINTS
[https://127.0.0.1:8000/admin/](https://127.0.0.1:8000/admin/)                <br>
[https://127.0.0.1:8000/api/](https://127.0.0.1:8000/api/)                    <br>
[https://127.0.0.1:8000/accounts/login/](https://127.0.0.1:8000/accounts/login)

## MIGRATIONS
make sure to follow this migrations order.
1. core
2. users
3. ...

## MISSING
accounts templates are missing
