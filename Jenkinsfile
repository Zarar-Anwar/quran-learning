pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        DJANGO_SETTINGS_MODULE = 'root.settings'
    }

    stages {
        stage('Setup Virtualenv') {
            steps {
                sh """
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    pip install -r requirements.txt
                """
            }
        }

        stage('Run Migrations') {
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    python manage.py makemigrations accounts website users courses
                    python manage.py migrate
                """
            }
        }

        stage('Start Dev Server') {
            steps {
                sh """
                    . ${VENV_DIR}/bin/activate
                    python manage.py runserver 0.0.0.0:8000
                """
            }
        }
    }
}