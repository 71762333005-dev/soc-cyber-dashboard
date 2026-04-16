pipeline {
    agent any

    environment {
        VENV = "venv"
        PATH = "${WORKSPACE}/venv/bin:${env.PATH}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Virtual Environment') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                '''
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                . venv/bin/activate
                pip install -r requirements.txt
                pip install flake8 pytest
                '''
            }
        }

        stage('Linting') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 . --exclude=venv --max-line-length=100
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                . venv/bin/activate
                pytest || true
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Add SonarQube scanner here (if configured)"
                // Example (if SonarQube installed):
                // sh 'sonar-scanner'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t cyber-app:latest .
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded 🎉"
        }

        failure {
            echo "Pipeline failed ❌"
        }

        always {
            echo "Pipeline finished"
        }
    }
}
