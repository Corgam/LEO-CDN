.PHONY: generate generate_workload run setup gsts clean compile_grpc_python coordinator

generate:
	@python ./generator.py

generate_workload:
	@python ./generate_workload.py

satellites:
	@sh ./temp/run-nodes.sh

setup: generate coordinator
		
gsts:
	@! docker ps -a | grep gsts || docker container rm gsts -f
	@docker build -f ./gsts/gsts.Dockerfile -t gsts .
	@docker run -it \
		--name gsts \
		--network=fredwork \
		--ip=172.26.8.5 \
		gsts

clean:
	@sh temp/clean.sh

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./satellite/proto/client.proto

coordinator:
# Run the coordinator and the simulation
	@! docker ps -a | grep coordinator || docker container rm coordinator -f
	@mkdir -p output/frames
	@rm -rf output/frames/*
	@docker build -f ./coordinator/coordinator.Dockerfile -t coordinator .
	@docker run -it \
		--name coordinator \
		-v $(CURDIR)/common/cert/keygroupPasser.crt:/common/cert/client.crt \
		-v $(CURDIR)/common/cert/keygroupPasser.key:/common/cert/client.key \
		-v $(CURDIR)/common/cert/ca.crt:/cert/ca.crt \
    	-v $(CURDIR)/temp/freds.json:/nodes.json \
		-v $(CURDIR)/output/:/output \
		-v $(CURDIR)/satellite/proto:/proto \
		-v $(CURDIR)/temp/:/temp \
		-v $(CURDIR)/config.toml:/config.toml \
		--network=fredwork \
		--ip=172.26.4.1 \
		coordinator
