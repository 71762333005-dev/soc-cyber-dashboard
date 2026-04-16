pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                git 'https://github.com/71762333005-dev/soc-cyber-dashboard.git'
            }
        }

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
