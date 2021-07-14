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
      export SAT_IP=$(${pkgs.iproute2}/bin/ip a | grep eth0 | head -2 | tail -1 | ${pkgs.gawk}/bin/awk '{print $4}')
      export CELESTIAL_GATEWAY=$(echo $SAT_IP | ${pkgs.gawk}/bin/awk -F"." '{printf "%d.%d.%d.%d", $1, $2, $3, $4 - 2}')
      ${pkgs.iproute2}/bin/ip r add default via $CELESTIAL_GATEWAY
      echo "nameserver $CELESTIAL_GATEWAY" | tee -a /etc/resolv.conf
      echo "nameserver 8.8.8.8" | tee -a /etc/resolv.conf
      echo $SAT_IP | tee -a /myip
    '';

    serviceConfig = {
      Type = "oneshot";
    };

    after = [ "dhcpcd.service" ];
    wantedBy = [ "multi-user.target" ];
  };

  networking.firewall.enable = false;

  systemd.services."import-docker" = {
    script = ''
      ${pkgs.docker}/bin/docker load < /fred/docker-fred.tar
      rm /fred/docker-fred.tar
    '';

    serviceConfig = {
      Type = "oneshot";
    };

    wantedBy = [ "multi-user.target" ];
  };

  systemd.services."frednode" = {
    script = ''
      sleep 20
      export SAT_IP=$(cat /myip)
      export SAT_HASH=$(echo $SAT_IP | sha1sum | ${pkgs.gawk}/bin/awk '{print substr($0,0,8)}')
      ${pkgs.docker}/bin/docker run -t -p 0.0.0.0:9001:9001 -p 0.0.0.0:5555:5555 --name fred fred \
      fred --log-level info \
        --handler dev \
        --nodeID $SAT_IP_HASH \
        --host $SAT_IP:9001 \
        --peer-host $SAT_IP:5555 \
        --adaptor badgerdb \
        --badgerdb-path ./db \
        --nase-host https://Berlin.gst.celestial:2379 \
        --nase-cert /cert/sat.crt \
        --nase-key /cert/sat.key \
        --nase-ca /cert/ca.crt \
        --trigger-cert /cert/sat.crt \
        --trigger-key /cert/sat.key \
        --trigger-ca /cert/ca.crt \
        --cert /cert/sat.crt \
        --key /cert/sat.key \
        --ca-file /cert/ca.crt \
        --auth-disable-rbac true
    '';

    after = [ "dhcpcd.service" "import-docker.service" ];
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
