{ config, pkgs, ... }:

{
  imports = [
    ./common.nix
  ];

  networking = {
    hostName = "SAT";
    interfaces."eth0".useDHCP = true;
  };
}
