
run_nodes:
	@docker network create fredwork --gateway 172.26.0.1 --subnet 172.26.0.0/16 || (exit 0)
	@docker-compose -f docker/etcd.yml  -f docker/node0.yml -f docker/node1.yml -f docker/node2.yml -f docker/node3.yml build
	@docker-compose --env-file .env -f docker/etcd.yml  -f docker/node0.yml -f docker/node1.yml -f docker/node2.yml -f docker/node3.yml up --force-recreate --abort-on-container-exit --renew-anon-volumes --remove-orphans

run_tester:
	@docker container rm keygroup-passer -f
	@docker build -f ./Dockerfile -t keygroup-passer .
	@docker run -it \
		--name keygroup-passer \
		-v $(CURDIR)/cert/keygroupPasser.crt:/cert/client.crt \
		-v $(CURDIR)/cert/keygroupPasser.key:/cert/client.key \
		-v $(CURDIR)/cert/ca.crt:/cert/ca.crt \
    -v $(CURDIR)/nodes.json:/nodes.json \
		--network=fredwork \
		--ip=172.26.4.1 \
		keygroup-passer

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./proto/client.proto

clean:
	@docker network rm fredwork
	@docker-compose -f docker/etcd.yml  -f docker/node0.yml -f docker/node1.yml -f docker/node2.yml -f docker/node3.yml down
