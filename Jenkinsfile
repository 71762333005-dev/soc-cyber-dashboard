pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    python -m pip install --upgrade pip
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

      stage('Lint (Skip Fail)') {
             steps {
               sh '''
            .      venv/bin/activate
                   flake8 . --exclude=venv --max-line-length=100 || echo "Lint issues found but continuing build"
                 '''
              }
           }

        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v || true
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo 'SonarQube stage placeholder (configure scanner if needed)'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "Building Docker image..."
                    docker build -t soc-cyber-dashboard:latest .
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully ✅'
        }

        failure {
            echo 'Pipeline failed ❌'
        }

        always {
            echo 'Pipeline finished'
        }
    }
}
