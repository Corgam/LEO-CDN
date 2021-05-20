.PHONY: generate_nodes run_nodes generate_and_run_nodes run_tester clean compile_grpc_python

generate_nodes:
	@python ./generator.py -node $(n)

run_nodes:
	@sh ./temp/run-nodes.sh

generate_and_run_nodes: generate_nodes run_nodes

run_tester:
	@! docker ps -a | grep leo-cdn-simulation || docker container rm leo-cdn-simulation -f
	@mkdir -p output/frames
	@rm -rf output/frames/*
	@docker build -f ./Dockerfile -t leo-cdn-simulation .
	@docker run -it \
		--name leo-cdn-simulation \
		-v $(CURDIR)/cert/keygroupPasser.crt:/cert/client.crt \
		-v $(CURDIR)/cert/keygroupPasser.key:/cert/client.key \
		-v $(CURDIR)/cert/ca.crt:/cert/ca.crt \
    -v $(CURDIR)/temp/nodes.json:/nodes.json \
		-v $(CURDIR)/output/:/output \
		--network=fredwork \
		--ip=172.26.4.1 \
		leo-cdn-simulation
	
run_server:
	@! docker ps -a | grep nodeserver || docker container rm nodeserver -f
	@docker build -f ./Dockerfile-serverTest -t nodeserver .
	@docker run -it \
		--name nodeserver \
		-v $(CURDIR)/temp/server1.crt:/cert/client.crt \
		-v $(CURDIR)/temp/server1.key:/cert/client.key \
		-v $(CURDIR)/cert/ca.crt:/cert/ca.crt \
    -v $(CURDIR)/temp/node1.json:/node.json \
		-v $(CURDIR)/output/:/output \
		--network=fredwork \
		--ip=172.26.8.3 \
		nodeserver
		
run_client:
	@! docker ps -a | grep nodeclient || docker container rm nodeclient -f
	@docker build -f ./Dockerfile-clientTest -t nodeclient .
	@docker run -it \
		--name nodeclient \
		--network=fredwork \
		--ip=172.26.8.4 \
		nodeclient

stardust:
	@! docker ps -a | grep stardust || docker container rm stardust -f
	@docker build -f ./Dockerfile-stardust -t stardust .
	@docker run -it \
		--name stardust \
		-v $(CURDIR)/cert/stardust.crt:/cert/stardust.crt \
		-v $(CURDIR)/cert/stardust.key:/cert/stardust.key \
		-v $(CURDIR)/cert/ca.crt:/cert/ca.crt \
    -v $(CURDIR)/temp/nodes.json:/temp/nodes.json \
		--network=fredwork \
		--ip=172.26.5.1 \
		stardust

clean:
	@sh temp/clean.sh

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./proto/client.proto
