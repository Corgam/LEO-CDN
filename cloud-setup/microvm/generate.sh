#!/bin/sh

genRootFs(){
    rm rootfs-${1}.ext4 2> /dev/null
    dd if=/dev/zero of=rootfs-${1}.ext4 bs=1M count=1500
    mkfs.ext4 rootfs-${1}.ext4

    mkdir /tmp/mnt-${1}
    sudo mount rootfs-${1}.ext4 /tmp/mnt-${1}
    sudo tar -xf $(nixos-generate -f lxc -c ${1}.nix) -C /tmp/mnt-${1}
    sudo umount /tmp/mnt-${1}
    rm -rf /tmp/mnt-${1}
}

for ROLE in sat gst loc
do
    genRootFs "$ROLE" &
done

wait