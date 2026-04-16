pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        SONAR_SCANNER_HOME = tool 'SonarScanner'   // Jenkins global tool name
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

        stage('Lint (Flake8)') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 . --exclude=venv --max-line-length=100 || true
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
                withSonarQubeEnv('soc-cyber') {
                    sh '''
                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=soc-cyber-dashboard \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=http://localhost:9000 \
                        -Dsonar.login=squ_8a05e60b748facf1c424191f2c37444de3ce96ef
                    '''
                }
            }
        }

    stage('Quality Gate') {
    steps {
        timeout(time: 10, unit: 'MINUTES') {
            script {
                def qg = waitForQualityGate()
                if (qg.status != 'OK') {
                    error "Failed Quality Gate: ${qg.status}"
                }
            }
        }
    }
}

        stage('Build Docker Image') {
            steps {
                sh '''
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
