pipeline {
    agent any

    environment {
        SONAR_TOKEN = credentials('soc-cyber-token')
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

        stage('Lint (Flake8)') {
            steps {
                sh '''
                . venv/bin/activate
                flake8 . --exclude=venv --max-line-length=120 --exit-zero
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                . venv/bin/activate
                PYTHONPATH=. pytest tests/ -v --junitxml=test-results.xml
                '''
            }
        }
         stage('SonarQube Analysis') {
             steps {
                 withSonarQubeEnv('soc-cyber') {
                 withCredentials([string(credentialsId: 'jenkins-soc', variable: 'SONAR_TOKEN')]) {
                 sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=soc-cyber-dashboard \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://192.168.1.102:9000 \
                    -Dsonar.login=$SONAR_TOKEN
                '''
            }
        }
    }
}

        stage('Quality Gate') {
            steps {
                timeout(time: 2, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker build -t soc-cyber-dashboard .
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
        success {
            echo "Pipeline SUCCESS ✅"
        }
        failure {
            echo "Pipeline failed ❌"
        }
    }
}
