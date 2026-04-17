pipeline {
    agent any

    environment {
        SONAR_TOKEN = credentials('jenkins-soc')
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
                pip install flake8 pytest pytest-cov
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

        stage('Unit Tests + Coverage') {
            steps {
                sh '''
                . venv/bin/activate
                PYTHONPATH=. pytest tests/ -v \
                --cov=. \
                --cov-report=xml:coverage.xml \
                --junitxml=test-results.xml
                '''
            }
        }

      stage('SonarQube Analysis') {
       steps {
        withSonarQubeEnv('soc-jenkins') {
            sh '''
            sonar-scanner \
            -Dsonar.projectKey=soc-cyber-dashboard \
            -Dsonar.sources=. \
            -Dsonar.host.url=http://192.168.1.102:9000 \
            -Dsonar.login=$SONAR_TOKEN \
            -Dsonar.python.coverage.reportPaths=coverage.xml \
            -Dsonar.exclusions=venv/**,**/__pycache__/**,**/*.csv,**/*.pkl
            '''
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
