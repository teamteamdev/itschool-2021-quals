{ name, domain }:

{ config, pkgs, lib, ... }:

with lib;

{
  imports = [ ../config-common.nix ];

  security.acme.certs.${domain} = {
    webroot = mkForce null;
    extraDomainNames = [ "*.${domain}" ];
    dnsProvider = "cloudflare";
    credentialsFile = "/root/ugractf/kyzylborda-secrets/cloudflare-api-keys";
  };

  services.nginx = {
    enable = true;
    virtualHosts."~^(?<task>.*)\\.${replaceStrings ["."] ["\\."] domain}" = {
      forceSSL = true;
      useACMEHost = domain;
      locations."/" = {
        # We don't use `proxyPass` to set custom Host header.
        extraConfig = ''
          proxy_pass http://unix:/var/lib/board_nti2021q-supervisor/http.sock;
          proxy_http_version 1.1;
          proxy_set_header Upgrade $http_upgrade;
          proxy_set_header Connection $connection_upgrade;
          proxy_set_header Host $task;
        '';
      };
    };
  };
}
