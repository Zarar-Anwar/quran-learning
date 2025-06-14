pipeline {
    agent any

    stages {

        stage('Build') {
            steps {
                echo 'Building Application'
            }
        }

        stage('Test') {
            when{
                expression{
                    BRANCH_NAME == 'zaala-dev'
                }
            }
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
