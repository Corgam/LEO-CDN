.PHONY: generate_nodes run_nodes generate_and_run_nodes run_tester clean compile_grpc_python

generate_nodes:
	@python ./generator.py -node $(n)

run_nodes:
	@sh ./temp/run-nodes.sh

generate_and_run_nodes: generate_nodes run_nodes

run_tester:
	@! docker ps -a | grep leo-cdn-simulation || docker container rm leo-cdn-simulation -f
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

clean:
	@sh temp/clean.sh

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./proto/client.proto
