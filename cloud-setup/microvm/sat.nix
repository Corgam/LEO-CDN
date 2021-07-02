{ config, pkgs, ... }:

{
  imports = [
    ./common.nix
  ];

  networking = {
    interfaces."eth0".useDHCP = true;
    nameservers = [
      "172.17.0.1"
    ];
  };
}
