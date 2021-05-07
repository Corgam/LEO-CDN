run_nodes:
#Check if the docker network "fredwork" is already created, if not create one.
	@docker network create fredwork --gateway 172.26.0.1 --subnet 172.26.0.0/16 || (exit 0)
	@docker-compose -f docker/etcd.yml -f docker/nodeB.yml -f docker/nodeC.yml build
	@docker-compose --env-file .env -f docker/etcd.yml -f docker/nodeB.yml -f docker/nodeC.yml up --force-recreate --abort-on-container-exit --renew-anon-volumes --remove-orphans

run_tester:
	@docker build -f ./Dockerfile -t keygroup-passer .
	@docker run -it \
		-v `pwd`/FReD/nase/tls/keygroupPasser.crt:/cert/client.crt \
		-v `pwd`/FReD/nase/tls/keygroupPasser.key:/cert/client.key \
		-v `pwd`/FReD/nase/tls/ca.crt:/cert/ca.crt \
		--network=fredwork \
		--ip=172.26.4.1 \
		keygroup-passer

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./proto/client.proto
