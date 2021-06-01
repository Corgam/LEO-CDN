.PHONY: generate run setup stardust clean compile_grpc_python coordinator

generate:
	@python ./generator.py

run:
	@sh ./temp/run-nodes.sh

setup: generate run
		
stardust:
	@! docker ps -a | grep stardust || docker container rm stardust -f
	@docker build -f ./stardust/stardust.Dockerfile -t stardust .
	@docker run -it \
		--name stardust \
		--network=fredwork \
		--ip=172.26.8.4 \
		stardust

clean:
	@sh temp/clean.sh

compile_grpc_python:
	@python -m grpc_tools.protoc -I . --python_out=. --grpc_python_out=. ./satellite/proto/client.proto

coordinator:
# Run the coordinator and the simulation
	@! docker ps -a | grep leo-cdn-simulation || docker container rm leo-cdn-simulation -f
	@mkdir -p output/frames
	@rm -rf output/frames/*
	@docker build -f ./coordinator/coordinator.Dockerfile -t leo-cdn-simulation .
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