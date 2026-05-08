pipeline {
    agent any
    environment {
        DOCKER_IMAGE = 'bogdansee/daily-brief'
        DOCKER_CREDENTIALS = 'dockerhub-credentials'
        TELEGRAM_TOKEN = credentials('telegram-alert-token')
        TELEGRAM_CHAT_ID = credentials('telegram-alert-chat-id')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} -t ${DOCKER_IMAGE}:latest ."
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "${DOCKER_CREDENTIALS}",
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh "echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin"
                    sh "docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}"
                    sh "docker push ${DOCKER_IMAGE}:latest"
                }
            }
        }

        stage('Deploy Morning') {
            steps {
                sh "kubectl create job deploy-morning-${BUILD_NUMBER} --from=cronjob/daily-brief-morning || true"
            }
        }

        stage('Deploy Noon') {
            steps {
                sh "kubectl create job deploy-noon-${BUILD_NUMBER} --from=cronjob/daily-brief-noon || true"
            }
        }

        stage('Deploy Evening') {
            steps {
                sh "kubectl create job deploy-evening-${BUILD_NUMBER} --from=cronjob/daily-brief-evening || true"
            }
        }
    }

    post {
        success {
            sh """
                curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
                -d chat_id=${TELEGRAM_CHAT_ID} \
                -d parse_mode=HTML \
                -d text="✅ <b>DailyBrief Build #${BUILD_NUMBER}</b> reusit!%0A📦 Imagine: ${DOCKER_IMAGE}:${BUILD_NUMBER}%0A⏱ Durata: ${currentBuild.durationString}"
            """
        }
        failure {
            sh """
                curl -s -X POST https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage \
                -d chat_id=${TELEGRAM_CHAT_ID} \
                -d parse_mode=HTML \
                -d text="❌ <b>DailyBrief Build #${BUILD_NUMBER}</b> a esuat!%0A🔍 Verifica: ${BUILD_URL}"
            """
        }
    }
}
