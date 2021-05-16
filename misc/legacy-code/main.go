package main

import (
	"context"
	"crypto/tls"
	"log"

	"github.com/ouzu/FReD-test/client"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
)

type fredNode struct {
	Name    string
	Address string
	tc      *credentials.TransportCredentials
	conn    *grpc.ClientConn
	Client  client.ClientClient
}

func (n *fredNode) Connect() error {
	log.Printf("Connecting to node '%s' at '%s'\n", n.Name, n.Address)
	conn, err := grpc.Dial(n.Address, grpc.WithTransportCredentials(*n.tc))
	if err != nil {
		return err
	}

	n.conn = conn
	n.Client = client.NewClientClient(conn)

	return nil
}

func (n *fredNode) Disconnect() {
	n.conn.Close()
}

func (n *fredNode) CreateKeygroup(name string) error {
	log.Printf("Creating Keygroup '%s' at node '%s'\n", name, n.Name)
	_, err := n.Client.CreateKeygroup(context.Background(), &client.CreateKeygroupRequest{
		Keygroup: name,
	})
	return err
}

func (n *fredNode) DeleteKeygroup(name string) error {
	log.Printf("Deleting Keygroup '%s' at node '%s'\n", name, n.Name)
	_, err := n.Client.DeleteKeygroup(context.Background(), &client.DeleteKeygroupRequest{
		Keygroup: name,
	})
	return err
}

func (n *fredNode) AddReplica(keygroup, replica string) error {
	log.Printf("Adding Replica '%s' to keygroup '%s' at node '%s'\n", replica, keygroup, n.Name)
	_, err := n.Client.AddReplica(context.Background(), &client.AddReplicaRequest{
		Keygroup: keygroup,
		NodeId:   replica,
	})
	return err
}

func (n *fredNode) RemoveReplica(keygroup, replica string) error {
	log.Printf("Removing Replica '%s' from keygroup '%s' at node '%s'\n", replica, keygroup, n.Name)
	_, err := n.Client.RemoveReplica(context.Background(), &client.RemoveReplicaRequest{
		Keygroup: keygroup,
		NodeId:   replica,
	})
	return err
}

func readTest(nodes ...*fredNode) {
	for _, n := range nodes {
		log.Printf("Reading at Id '0' from Keygroup 'test' at node '%s'\n", n.Name)

		readResp, err := n.Client.Read(context.Background(), &client.ReadRequest{
			Keygroup: "test",
			Id:       "0",
		})

		if err != nil {
			log.Println(err)
		} else {
			log.Println(readResp.String())
		}
	}
}

func writeTest(node *fredNode) {
	log.Printf("Appending '123456' to Keygroup 'test' at node '%s'\n", node.Name)

	appendResp, err := node.Client.Append(context.Background(), &client.AppendRequest{
		Keygroup: "test",
		Data:     "123456",
	})

	if err != nil {
		log.Println(err)
	} else {
		log.Println(appendResp.String())
	}
}

func main() {
	cert, err := tls.LoadX509KeyPair("../FReD/nase/tls/client.crt", "../FReD/nase/tls/client.key")

	if err != nil {
		log.Fatal("Cannot load certificates")
	}

	tlsConfig := &tls.Config{
		Certificates:       []tls.Certificate{cert},
		MinVersion:         tls.VersionTLS12,
		InsecureSkipVerify: true,
	}

	tc := credentials.NewTLS(tlsConfig)

	node2 := &fredNode{
		Name:    "fred",
		Address: "172.26.1.2:9001",
		tc:      &tc,
	}

	err = node2.Connect()
	if err != nil {
		log.Fatal(err)
	}

	defer node2.Disconnect()

	node3 := &fredNode{
		Name:    "fred3",
		Address: "172.26.1.3:9001",
		tc:      &tc,
	}

	err = node3.Connect()
	if err != nil {
		log.Fatal(err)
	}
	defer node3.Disconnect()

	err = node2.CreateKeygroup("test")
	if err != nil {
		log.Println(err)
	}

	readTest(node2, node3)

	writeTest(node2)

	readTest(node2, node3)

	err = node2.AddReplica("test", node3.Name)
	if err != nil {
		log.Println(err)
	}

	readTest(node2, node3)

	err = node2.RemoveReplica("test", node2.Name)
	if err != nil {
		log.Println(err)
	}

	err = node3.RemoveReplica("test", node2.Name)
	if err != nil {
		log.Println(err)
	}

	readTest(node2, node3)

	err = node3.DeleteKeygroup("test")
	if err != nil {
		log.Println(err)
	}

	readTest(node2, node3)
}
