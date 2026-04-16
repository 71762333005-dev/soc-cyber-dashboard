pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Test') {
            steps {
                sh '''
                . venv/bin/activate
                python predict.py || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cyber-app:latest .'
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
    }
}
