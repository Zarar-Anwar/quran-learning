pipeline {
    agent any

    environment {
        VENV_DIR = 'venv'
        DJANGO_SETTINGS_MODULE = 'root.settings'
        SERVER_PORT = '8000'
    }

    stages {
        stage('Setup Virtualenv') {
            steps {
                sh '''
                    python -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Migrations') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python manage.py makemigrations accounts website users courses
                    python manage.py migrate
                '''
            }
        }

        stage('Start Dev Server') {
            steps {
                script {
                    sh """
                        . ${VENV_DIR}/bin/activate
                        echo "Starting Django development server..."
                        nohup python manage.py runserver 0.0.0.0:${SERVER_PORT} > server.log 2>&1 &
                        echo \$! > server.pid
                        sleep 5
                        echo "Server started with PID \$(cat server.pid)"
                        echo "Access at: http://localhost:${SERVER_PORT}"
                        echo "View logs with: tail -f server.log"
                    """
                }
            }
        }

        stage('Verify Server') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "Verifying server is running..."
                    curl -I http://localhost:${SERVER_PORT} || true
                '''
                sleep 30
            }
        }
    }

    post {
        always {
            script {
                sh """
                    echo "Cleaning up..."
                    if [ -f server.pid ]; then
                        echo "Stopping server with PID \$(cat server.pid)"
                        kill \$(cat server.pid) || true
                        rm -f server.pid
                    fi
                    echo "Current server processes:"
                    ps aux | grep runserver || true
                """
            }
        }
        success {
            echo 'Pipeline completed successfully'
        }
        failure {
            echo 'Pipeline failed - check logs for details'
        }
    }
}