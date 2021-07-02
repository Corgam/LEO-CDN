{ config, pkgs, ... }:

{
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

  services.nginx.virtualHosts."0.0.0.0" = {
    addSSL = false;
    locations."/".return = "200 OK\n";
  };

  services.haveged.enable = true;
  services.openssh.enable = true;

  nix.autoOptimiseStore = true;

  environment.systemPackages = with pkgs; [
    vim
  ];
}
