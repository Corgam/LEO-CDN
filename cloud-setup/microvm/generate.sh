#!/bin/sh

genRootFs(){
    rm rootfs-${1}.ext4 2> /dev/null
    rm rootfs-${1}.ext4.zst 2> /dev/null
    dd if=/dev/zero of=rootfs-${1}.ext4 bs=1M count=1100
    mkfs.ext4 rootfs-${1}.ext4

    mkdir /tmp/mnt-${1}
    sudo mount rootfs-${1}.ext4 /tmp/mnt-${1}
    sudo tar -xf $(nixos-generate -f lxc -c ${1}.nix) -C /tmp/mnt-${1}
    sudo umount /tmp/mnt-${1}
    rm -rf /tmp/mnt-${1}

    if [ "$1" != "loc" ]; then
        tar --remove-files --zstd -cf rootfs-${1}.tar.zst rootfs-${1}.ext4
    fi
}

for ROLE in sat gst loc
do
    genRootFs "$ROLE" &
done

wait