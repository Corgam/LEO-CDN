.PHONY: generate_nodes run_nodes generate_and_run_nodes run_tester clean compile_grpc_python

generate_nodes:
	@python ./generator.py -node $(n)

run_nodes:
	@sh ./temp/run-nodes.sh

generate_and_run_nodes: generate_nodes run_nodes

run_tester:
	@! docker ps -a | grep keygroup-passer || docker container rm keygroup-passer -f
	@docker build -f ./Dockerfile -t keygroup-passer .
	@docker run -it \
		--name keygroup-passer \
		-v $(CURDIR)/cert/keygroupPasser.crt:/cert/client.crt \
		-v $(CURDIR)/cert/keygroupPasser.key:/cert/client.key \
		-v $(CURDIR)/cert/ca.crt:/cert/ca.crt \
    -v $(CURDIR)/temp/nodes.json:/nodes.json \
		--network=fredwork \
		--ip=172.26.4.1 \
		keygroup-passer

clean:
	@sh temp/clean.sh

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./proto/client.proto
