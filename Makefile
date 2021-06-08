.PHONY: generate run setup stardust clean compile_grpc_python coordinator

generate:
	@python ./generator.py

run:
	@sh ./temp/run-nodes.sh

setup: generate run
		
stardust:
	@sh ./temp/run-stardusts.sh

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