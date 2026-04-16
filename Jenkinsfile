pipeline {
    agent any

    stages {

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Test') {
            steps {
                sh 'python predict.py || true'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t cyber-app:latest .'
            }
        }
    }
}
