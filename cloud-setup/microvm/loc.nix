# This contains the network configuration for local testing

{ config, pkgs, ... }:

{
  imports = [
      ./common.nix
  ];

  networking.interfaces.eth0.ipv4.addresses = [{
    address = "172.17.100.1";
    prefixLength = 16;
  }];

  networking.defaultGateway = "172.17.0.1";
  networking.nameservers = [ "1.1.1.1" ];
}
