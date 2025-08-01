docker pull $DOCKERHUB_USERNAME/server:latest
docker stop server || true
docker rm server || true
docker run -d --name server -p 80:80 $DOCKERHUB_USERNAME/server:latest