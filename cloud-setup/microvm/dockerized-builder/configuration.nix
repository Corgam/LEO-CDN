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

  environment.systemPackages = with pkgs; [
    vim
  ];
}
