{ config, pkgs, ... }:

{
  imports = [ ];
  boot.isContainer = true;

  users = {
    mutableUsers = false;
    users = {
      user = {
        isNormalUser = true;
        home = "/home/user";
        extraGroups = [ "wheel" ];
        uid = 1000;
        password = "leocdn";
      };

      root = {
        hashedPassword = "*";
      };
    };
  };

  services.nginx.enable = true;
  networking.firewall.allowedTCPPorts = [ 80 ];

  environment.systemPackages = with pkgs; [
    vim
  ];
}
