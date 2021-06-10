# GCP Celestial setup

## Prerequisites

### GCP access
You need to be a member of the GCP project and [add your SSH key](https://console.cloud.google.com/compute/metadata/sshKeys?project=leo-cdn&folder&organizationId) to the project.

To give Ansible access to the GCP resources, we created a service account named ansible. New access keys can be generated [here](https://console.cloud.google.com/iam-admin/serviceaccounts/details/109872545193777506173/keys?project=leo-cdn) and must be saved at `cloud-setup/gcp.json`.

It can be useful to have the `gcloud` CLI tool installed as the web interface is rather complicated.

### Ansible

To run the cloud setup, you need to have Ansible installed on your machine.

The required ansible modules can be installed using `ansible-galaxy collection install ansible.posix community.general google.cloud gantsign.golang`.

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