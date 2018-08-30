pipeline {
    agent any

    stages {
        stage('Python 2.7 - Testing') {
            steps {
                withPythonEnv('/usr/bin/python2.7') {
                    echo 'Running test suite for Python 2.7'
                    sh 'pip install -r requirements.txt'
                    sh 'py.test --cov=sportsreference --cov-report term-missing tests/'
                }
            }
        }
        stage('Python 2.7 - Building') {
            steps {
                withPythonEnv('/usr/bin/python2.7') {
                    echo 'Building PIP wheel for Python 2.7'
                }
            }
        }
    }
}
