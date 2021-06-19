#!/bin/sh

FC_PROJECT=leo-cdn

FC_REGION=europe-west3
FC_ZONE=europe-west3-c

FC_VDISK=disk-dbuster
FC_IMAGE=dbuster-nested-kvm

FC_INSTANCE=celestial-vm

gcloud config set project ${FC_PROJECT}

gcloud config set compute/region ${FC_REGION}
gcloud config set compute/zone ${FC_ZONE}

if gcloud compute disks list | grep ${FC_VDISK}; then
	echo "Disk ${FC_VDISK} already exists"
else
	echo "Creating disk ${FC_VDISK}"
	gcloud compute disks create ${FC_VDISK} \
		--image-project debian-cloud --image-family debian-10 --zone=${FC_ZONE}
fi

if gcloud compute images list | grep ${FC_IMAGE}; then
	echo "Image ${FC_IMAGE} already exists"
else
	echo "Creating image ${FC_IMAGE}"
	gcloud compute images create ${FC_IMAGE} --source-disk ${FC_VDISK} \
		--source-disk-zone ${FC_ZONE} \
		--licenses "https://www.googleapis.com/compute/v1/projects/vm-options/global/licenses/enable-vmx"
fi

if gcloud compute instances list | grep ${FC_INSTANCE}; then
	echo "Instance ${FC_INSTANCE} already exists"
else
	echo "Creating instance ${FC_INSTANCE}"
	gcloud compute instances create ${FC_INSTANCE} --zone=${FC_ZONE} \
		--min-cpu-platform "Intel Haswell" \
		--image ${FC_IMAGE}
fi
