pipeline {
  agent any
  stages {
    stage('Container Build') {
      parallel {
        stage('Container Build') {
          steps {
            echo 'Building..'
          }
        }
		stage('Building tng-sdk-analysis-weight') {
          steps {
            sh 'docker build -t registry.sonata-nfv.eu:5000/tng-sdk-analysis-weight -f sla-template-generator/Dockerfile .'
          }
		}
      }
    }
    stage('Unit Tests') {
      parallel {
        stage('Unit Tests') {
          steps {			
            echo 'Unit Testing..'
          }
        }
        stage('Unit tests for tng-sdk-analysis-weight') {
          steps {
            sh 'mvn clean test -f sla-template-generator'
          }
        }
      }
    }
    stage('Code Style check') {
      parallel {
        stage('Code Style check') {
          steps {
            echo 'Code Style check....'
          }
        }
        stage('Code check for tng-sdk-analysis-weight') {
          steps {
             sh 'mvn site -f sla-template-generator'
          }
        }
      }
    }
    stage('Containers Publication') {
      parallel {
        stage('Containers Publication') {
          steps {
            echo 'Publication of containers in local registry....'
          }
        }
		stage('Publishing tng-sdk-analysis-weight') {
          steps {
            sh 'docker push registry.sonata-nfv.eu:5000/tng-sdk-analysis-weight'
          }
		}
      }
    }	
	
	stage('Deployment in Pre-Integration') {
          parallel {
            stage('Deployment in Pre-Integration') {
              steps {
                echo 'Deploying in Pre-integration...'
              }
            }
            stage('Deploying') {
              steps {
                sh 'rm -rf tng-devops || true'
                sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
                dir(path: 'tng-devops') {
                  sh 'ansible-playbook roles/sp.yml -i environments -e "target=pre-int-sp host_key_checking=False component=sla-management"'
                }
              }
            }
          }
	}
	
	stage('Promoting to integration') {
      when{
        branch 'master'
      }      
      steps {
        sh 'docker tag registry.sonata-nfv.eu:5000/tng-sdk-analysis-weight:latest registry.sonata-nfv.eu:5000/tng-sdk-analysis-weight:int'
        sh 'docker push registry.sonata-nfv.eu:5000/tng-sdk-analysis-weight:int'
        sh 'rm -rf tng-devops || true'
        sh 'git clone https://github.com/sonata-nfv/tng-devops.git'
        dir(path: 'tng-devops') {
		  sh 'ansible-playbook roles/sp.yml -i environments -e "target=int-sp component=sla-management"'
        }
      }
    }

  }
  
  post {
         success {
                 emailext(from: "jenkins@sonata-nfv.eu", 
                 to: "mtouloup@unipi.gr", 
                 subject: "SUCCESS: ${env.JOB_NAME}/${env.BUILD_ID} (${env.BRANCH_NAME})",
                 body: "${env.JOB_URL}")
         }
         failure {
                 emailext(from: "jenkins@sonata-nfv.eu", 
                 to: "mtouloup@unipi.gr", 
                 subject: "FAILURE: ${env.JOB_NAME}/${env.BUILD_ID} (${env.BRANCH_NAME})",
                 body: "${env.JOB_URL}")
         }
    }
}
