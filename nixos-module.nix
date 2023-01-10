{ pkgs, lib, config, ... }:
let
  cfg = config.services.catgpt;
  defaultUser = "catgpt";
in with lib; {
  options.services.catgpt = {
    enable = mkEnableOption "catgpt";
    user = mkOption {
      type = types.str;
      description = "User to run under";
      default = defaultUser;
    };
    group = mkOption {
      type = types.str;
      description = "Group to run under";
      default = defaultUser;
    };
    server = mkOption {
      type = types.str;
      description = "Fediverse server to post to";
      example = "https://fedi.astrid.tech";
    };
    postOnCalendar = mkOption {
      type = types.str;
      description = "systemd OnCalendar specification";
      default = "*-*-* *:30:00";
    };
    accessTokenFile = mkOption {
      type = types.path;
      description = ''
        Path to file containing the access token.

        To generate one, see here: https://prplecake.github.io/pleroma-access-token/
      '';
      default = "/var/lib/secrets/catgpt/accessToken";
    };
  };

  config = mkIf cfg.enable {
    systemd.services.catgpt-config = {
      description = "Set up catgpt required directories";
      environment = { inherit (cfg) user group accessTokenFile; };

      script = ''
        mkdir -p "$(dirname "$accessTokenFile")"
        chown -R "$user:$group" "$(dirname "$accessTokenFile")"
      '';
    };

    systemd.services.catgpt = {
      description = "Technology Prediction Pleroma Bot";
      wants = [ "catgpt-config.service" ];
      path = with pkgs; [ catgpt ];
      environment = {
        SERVER_URL = cfg.server;
        ACCESS_TOKEN_PATH = cfg.accessTokenFile;
      };

      script = ''
        export ACCESS_TOKEN="$(cat "$ACCESS_TOKEN_PATH")"
        ${pkgs.catgpt}/bin/catgpt.py
      '';

      unitConfig = {
        # Access token file must exist to run this service 
        ConditionPathExists = [ cfg.accessTokenFile ];
      };

      serviceConfig = {
        User = cfg.user;
        Group = cfg.group;
      };
    };

    systemd.timers.catgpt = {
      wantedBy = [ "network-online.target" ];
      timerConfig.OnCalendar = cfg.postOnCalendar;
    };

    users.users = optionalAttrs (cfg.user == defaultUser) {
      ${defaultUser} = {
        group = cfg.group;
        isSystemUser = true;
      };
    };

    users.groups =
      optionalAttrs (cfg.group == defaultUser) { ${defaultUser} = { }; };
  };
}
