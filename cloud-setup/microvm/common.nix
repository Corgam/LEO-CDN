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

  services.mysql = {
    enable = true;
    package = pkgs.mariadb;
  };

  virtualisation.docker.enable = true;

  systemd.services."celestial-network" = {
    script = ''
      sleep 10
      export CELESTIAL_GATEWAY=$(${pkgs.iproute2}/bin/ip a | grep eth0 | head -2 | tail -1 | ${pkgs.gawk}/bin/awk '{print $4}' | ${pkgs.gawk}/bin/awk -F"." '{printf "%d.%d.%d.%d", $1, $2, $3, $4 - 2}')
      ${pkgs.iproute2}/bin/ip r add default via $CELESTIAL_GATEWAY
      echo "nameserver $CELESTIAL_GATEWAY" | tee -a /etc/resolv.conf
      echo "nameserver 8.8.8.8" | tee -a /etc/resolv.conf
    '';

    serviceConfig = {
      Type = "oneshot";
    };

    after = [ "dhcpcd.service" ];
    wantedBy = [ "multi-user.target" ];
  };

  services.haveged.enable = true;
  services.openssh.enable = true;

  nix.autoOptimiseStore = true;

  environment.systemPackages = with pkgs; [
    vim
    ldns
    python
  ];
}
