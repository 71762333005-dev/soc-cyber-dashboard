pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
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
                      flake8 . --exclude=venv --max-line-length=100 --exit-zero
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v
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
                        echo "Quality Gate Status: ${qg.status}"

                        if (qg.status != 'OK') {
                            error "Quality Gate Failed: ${qg.status}"
                        }
                    }
                }
            }
        }

        stage('Strict Production Gate') {
            steps {
                script {
                    echo "Enforcing STRICT production rules via SonarQube Quality Gate..."

                    def qg = waitForQualityGate()

                    if (qg.status != 'OK') {
                        error "STRICT GATE FAILED ❌ (Bugs or Vulnerabilities detected)"
                    } else {
                        echo "STRICT GATE PASSED ✅"
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
