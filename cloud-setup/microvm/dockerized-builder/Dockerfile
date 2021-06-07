FROM nixos/nix

RUN nix-channel --add https://nixos.org/channels/nixos-20.09/ nixos
RUN nix-channel --update

RUN nix-env -iA nixos.nixos-generators

ADD generate.sh /builder/
ADD configuration.nix /builder/

ENTRYPOINT [ "sh", "-c", "/builder/generate.sh" ]