{ config, pkgs, ... }:

let
  naseIP = "10.255.0.2";

  clientPort = 2379;
  peerPort = 2380;
in
{
  imports = [
    ./common.nix
  ];

  networking = {
    hostName = "GST";
    interfaces."eth0".useDHCP = true;
    firewall.allowedTCPPorts = [
      clientPort
      peerPort
    ];
  };

  services.etcd = {
    enable = true;
    name = "s-1";
    dataDir = "/tmp/etcd/s-1";

    listenClientUrls = [ "http://${naseIP}:${toString clientPort}" ];
    advertiseClientUrls = [ "http://${naseIP}:${toString clientPort}" ];

    listenPeerUrls = [ "http://${naseIP}:${toString peerPort}" ];
    initialAdvertisePeerUrls = [ "http://${naseIP}:${toString peerPort}" ];

    certFile = "/cert/gst.crt";
    keyFile = "/cert/gst.key";

    trustedCaFile = "/cert/ca.crt";

    clientCertAuth = true;

    initialCluster = [ "s-1=http://${naseIP}:${toString peerPort}" ];
    initialClusterToken = "tkn";
  };
}
