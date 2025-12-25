FROM jenkins/jenkins:lts

USER root

# Install Docker CLI using official script (safe for Debian)
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    curl -fsSL https://get.docker.com | sh && \
    apt-get clean

# Allow Jenkins to run Docker commands
RUN usermod -aG docker jenkins

USER jenkins
