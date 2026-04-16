pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        SONAR_SCANNER_HOME = tool 'SonarScanner'
        SONAR_HOST = "http://localhost:9000"
        SONAR_PROJECT_KEY = "soc-cyber-dashboard"
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
                    pip install flake8 pytest requests
                '''
            }
        }

        stage('Lint (Flake8)') {
            steps {
                sh '''
                    . venv/bin/activate
                    flake8 . --exclude=venv --max-line-length=100
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
                    sh """
                        ${SONAR_SCANNER_HOME}/bin/sonar-scanner \
                        -Dsonar.projectKey=${SONAR_PROJECT_KEY} \
                        -Dsonar.sources=. \
                        -Dsonar.host.url=${SONAR_HOST} \
                        -Dsonar.login=${SONAR_AUTH_TOKEN}
                    """
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 10, unit: 'MINUTES') {
                    script {
                        def qg = waitForQualityGate()
                        if (qg.status != 'OK') {
                            error "❌ Sonar Quality Gate FAILED: ${qg.status}"
                        }
                    }
                }
            }
        }

        stage('Strict Production Gate') {
            steps {
                script {
                    def response = sh(
                        script: """
                        curl -s -u ${SONAR_AUTH_TOKEN}: \
                        "${SONAR_HOST}/api/measures/component?component=${SONAR_PROJECT_KEY}&metricKeys=bugs,vulnerabilities"
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Sonar Metrics Response: ${response}"

                    def json = readJSON text: response
                    def measures = json.component.measures

                    int bugs = 0
                    int vulns = 0

                    for (m in measures) {
                        if (m.metric == "bugs") {
                            bugs = m.value.toInteger()
                        }
                        if (m.metric == "vulnerabilities") {
                            vulns = m.value.toInteger()
                        }
                    }

                    echo "Bugs: ${bugs}"
                    echo "Vulnerabilities: ${vulns}"

                    if (bugs > 0 || vulns > 0) {
                        error "❌ STRICT PRODUCTION GATE FAILED: Bugs=${bugs}, Vulnerabilities=${vulns}"
                    }

                    echo "✅ Strict Production Gate PASSED"
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
