# GCP Celestial setup

## Prerequisites

### GCP access
You need to be a member of the GCP project and [add your SSH key](https://console.cloud.google.com/compute/metadata/sshKeys?project=leo-cdn&folder&organizationId) to the project.

To give Ansible access to the GCP resources, we created a service account named ansible. New access keys can be generated [here](https://console.cloud.google.com/iam-admin/serviceaccounts/details/109872545193777506173/keys?project=leo-cdn) and must be saved at `cloud-setup/gcp.json`.

It can be useful to have the `gcloud` CLI tool installed as the web interface is rather complicated.

### Ansible

To run the cloud setup, you need to have Ansible installed on your machine.

The required ansible modules can be installed using `ansible-galaxy collection install ansible.posix community.general google.cloud gantsign.golang andrewrothstein.firecracker geerlingguy.docker`.

Note: In case `gantsign.golang` or `andrewrothstein.firecracker` or `geerlingguy.docker` cannot be found, install them via: `ansible-galaxy install andrewrothstein.firecracker gantsign.golang geerlingguy.docker`.

## Starting the VM

There are 2 ansible playbooks.

The setup does
- Setup the needed GCP resources
- Start a new GCP instances
- Install the required software
- Copy Celestial to the instance

And the teardown does
- Remove the GCP instance and resources
- Remove the SSH key from the local known_hosts

If you want to run the full setup, you need to run `ansible-playbook setup.yml`. This will take about 10 minutes.

You can also just run the celestial setup using `ansible-playbook --tags celestial setup.yml`.

To do the full teardown, you need to run `ansible-playbook teardown.yml`. If you just want to delte the instance, you can run `ansible-playbook --tags instance teardown.yml`. This is useful to test changes in the playbook or if something got messed up on the instance. As Ansible operations are idempotent, you can just run the setup again after running the partial teardown and it will skip the other steps.

## Starting celestial

The celestial server needs to be started manually for now.

To keep the simulation running without an active SSH session, you can use `tmux`.

To do so, log in via ssh:

`ssh 34.89.212.29`

and start celestial:

`cd celestial`

`make binary`

`make runserver`

and in a separate shell:

`cd celestial`

`make container`

`sudo docker run -p 8000:8000 --rm -it -v /config.toml:/config.toml celestial /config.toml`

## Working in the VM environment
### The Celestial APIs

The `drill` DNS client is available to interact with Celestials [DNS API](https://github.com/OpenFogStack/celestial#dns-api).

`drill @127.0.0.1 0.0.celestial`

`drill @127.0.0.1 Berlin.gst.celestial`

The [HTTP API](https://github.com/OpenFogStack/celestial#http-api) can be queried using `curl`

`curl localhost/info`

`curl localhost/shell/0/0`
### Interacting with the MicroVMs

We can login to the microvms using ssh. The username is `user` and password `leocdn`.

## building the rootfs and kernel

Rootfs and kernel can be downloaded using the `dl-microvm.sh` script.

The rootfs can also be built using the builder in the `microvm` directory.

Note: In case the files take too long, try downloading them via browser.

### state of the rootfs

The rootfs doesn't contain our application yet.

The DNS server needs to be configured to Celestial.




The current rootfs is way too large.

We need to create a smaller file system and maybe also reduce the size of the image content.

For now, the image needs some free space to store data at microvm runtime though.

Tobias mentioned that it may be possible at some point to mount a separate image for the data to each microvm and even use images with dynamic size.

## gcloud
Some useful commands are listed below:

### Set the project
`gcloud config set project leo-cdn`

### List all instances
`gcloud compute instances list`

### SSH into an instance
`gcloud compute ssh celestial-vm`

### Delete all instances
`gcloud compute instances delete $(gcloud compute instances list --project leo-cdn | awk '(NR>1) {print $1}')`

## local testing

We use the existing docker bridge to minimize messing around with the network settings.

(rootfs)[https://ipfs.io/ipfs/QmfSekKPHgS38KPLQWQuU7w8DPTqEqmcUQKYRJo18Tzv5z?filename=rootfs-loc.ext4.zst]

Create a new tap device

`sudo ip tuntap add veth0 mode tap`

Add it to the docker bridge

`sudo brctl addif docker0 veth0`

Get the MAC adress

`ip a | grep -A1 veth0 | grep ether`

Start microvm (insert MAC)

`firectl --kernel=hello-vmlinux.bin --root-drive=rootfs-loc.ext4 --tap-device=veth0/xx:xx:xx:xx:xx:xx`