.PHONY: generate run setup gsts clean compile_grpc_python coordinator

test:
	@! docker ps -a | grep stardust || docker container rm stardust -f
	@docker build -f ./stardust/stardust.Dockerfile -t stardust .
	@docker run -it \
		--name stardust \
		--network=fredwork \
		--ip=172.26.8.4 \
		stardust

generate:
	@python ./generator.py

satellites:
	@sh ./temp/run-nodes.sh

setup: generate coordinator
		
gsts:
	@! docker ps -a | grep gsts || docker container rm gsts -f
	@docker build -f ./gsts/gsts.Dockerfile -t gsts .
	@docker run -it \
		--name gsts \
		--network=fredwork \
		--ip=172.26.8.4 \
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