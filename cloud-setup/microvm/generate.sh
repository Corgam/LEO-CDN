rm rootfs.ext4
dd if=/dev/zero of=rootfs.ext4 bs=1M count=1500
mkfs.ext4 rootfs.ext4
sudo mount rootfs.ext4 mnt
sudo tar -xf $(nixos-generate -f lxc -c configuration.nix) -C mnt
sudo umount mnt
