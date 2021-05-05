# FReD Test

## what works
- Creating a keygroup
- Adding data to the keygroup
- Reading data from a keygroup
- Adding a replica node to a keygroup
- Deleting a keygroup

## what doesn't work
- Removing the node which created the keygroup from the keygroups replica nodes

# Docker setup

I created the containers manually for now and used the commands from the FReD readme. Docker compose will be used later.

NaSe:
```sh
docker run -d \
-v $(pwd)/nase/tls/etcdnase.crt:/cert/etcdnase.crt \
-v $(pwd)/nase/tls/etcdnase.key:/cert/etcdnase.key \
-v $(pwd)/nase/tls/ca.crt:/cert/ca.crt \
--network=fredwork \
--ip=172.26.1.1 --name NaSe \ 
quay.io/coreos/etcd:v3.4.10 \
etcd --name s-1 \      
--data-dir /tmp/etcd/s-1 \
--listen-client-urls https://172.26.1.1:2379 \
--advertise-client-urls https://172.26.1.1:2379 \
--listen-peer-urls http://172.26.1.1:2380 \
--initial-advertise-peer-urls http://172.26.1.1:2380 \
--initial-cluster s-1=http://172.26.1.1:2380 \
--initial-cluster-token tkn \        
--initial-cluster-state new \   
--cert-file=/cert/etcdnase.crt \
--key-file=/cert/etcdnase.key \
--client-cert-auth \               
--trusted-ca-file=/cert/ca.crt
```

FReD nodes:
```sh
docker run -d \
-v $(pwd)/nase/tls/frednode.crt:/cert/frednode.crt \
-v $(pwd)/nase/tls/frednode.key:/cert/frednode.key \
-v $(pwd)/nase/tls/ca.crt:/cert/ca.crt \
--network=fredwork \
--ip=172.26.1.2 --name FReD1 \
fred \
fred --log-level info \
--handler dev \
--nodeID fred \
--host 172.26.1.2:9001 \
--peer-host 172.26.1.2:5555 \
--adaptor badgerdb \
--badgerdb-path ./db \
--nase-host https://172.26.1.1:2379 \
--nase-cert /cert/frednode.crt \
--nase-key /cert/frednode.key \
--nase-ca /cert/ca.crt \
--trigger-cert /cert/frednode.crt \
--trigger-key /cert/frednode.key \
--cert /cert/frednode.crt \
--key /cert/frednode.key \
--ca-file /cert/ca.crt
```

```sh
docker run -d \
-v $(pwd)/nase/tls/frednode.3.crt:/cert/frednode.crt \
-v $(pwd)/nase/tls/frednode.3.key:/cert/frednode.key \
-v $(pwd)/nase/tls/ca.crt:/cert/ca.crt \
--network=fredwork \
--ip=172.26.1.3 --name FReD3 \
fred \
fred --log-level info \
--handler dev \
--nodeID fred3 \
--host 172.26.1.3:9001 \
--peer-host 172.26.1.3:5555 \
--adaptor badgerdb \
--badgerdb-path ./db \
--nase-host https://172.26.1.1:2379 \
--nase-cert /cert/frednode.crt \
--nase-key /cert/frednode.key \
--nase-ca /cert/ca.crt \
--trigger-cert /cert/frednode.crt \
--trigger-key /cert/frednode.key \
--cert /cert/frednode.crt \
--key /cert/frednode.key \
--ca-file /cert/ca.crt
```

Certificates:
```sh
bash gen-cert.sh frednode.3 172.26.1.3
```

```sh
bash gen-cert.sh client 172.26.0.1
```