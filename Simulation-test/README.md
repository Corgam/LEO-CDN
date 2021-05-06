# Simulation-test

Starts two FReD nodes (`nodeB` and `nodeC`, corresponding to the nodes in the `FReD` tests) and a client (`tester`) that initializes a keygroup that is continuously passed between the two nodes.

* Fix key usage and generate certificates
  * Fix key usage in `FReD/nase/tls/gen-cert.sh`
    * add `digitalSignature` so it looks like `keyUsage = keyEncipherment, dataEncipherment, digitalSignature`
    * see for details https://superuser.com/a/1248085
  * Generate certificates
    * `cd FReD/nase/tls/`
    * `sh gen-cert.sh nodeBx 172.26.2.1`
    * `sh gen-cert.sh nodeCx 172.26.3.1`
    * `sh gen-cert.sh keygroupPasser 172.26.4.1`
* Generate Python gRPC client: `make compile_grpc_python`
* Start FReD nodes and NaSe: `run_nodes`
* Start tester: `run_tester`
