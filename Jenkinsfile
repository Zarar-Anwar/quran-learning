pipeline {
    agent any

    environment {
        NEW_VERSION = '1.3.5'
        SERVER_CREDENTIALS = credentials('zaala_websites')
    }

    stages {

        stage('Build') {
            steps {
                echo 'Building Application'
                echo "Server Credentials are ${SERVER_CREDENTIALS}"
            }
        }

        stage('Test') {
//             when{
//                 expression{
//                     BRANCH_NAME == 'zaala-dev'
//                 }
//             }
            steps {
                 echo 'Testing Application'
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying Application'
            }
        }
    }
    post{
            always{
            echo 'Always'
            }
            success{
            echo 'On Success I Run'
            }
            failure{
            echo 'On Failure I Run'
            }
        }
}
