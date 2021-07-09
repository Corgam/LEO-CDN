#!/bin/sh

docker build -t fred ../../FReD
docker build -t fredstore -f ../../FReD/storage.Dockerfile ../../FReD
docker build -t sat -f ../../satellite/satellite.Dockerfile ../../satellite

docker save fred > docker-fred.tar
docker save fredstore > docker-fredstore.tar
docker save sat > docker-sat.tar