#!/bin/bash
# Creates or updates the site's Compose (deploy/compose.yml) in Dokploy, deploys it and checks
# it. Runs ON the VPS as facchini (sudo without a password); deploy/apply.sh copies it there and
# runs it. Safe to run again: it updates what exists.
#
# The HTTPS certificates come from Let's Encrypt (Dokploy's Traefik) once the DNS of
# www.facchini.eti.br and facchini.eti.br points to this server. Before that the site already
# answers here (checked through Traefik on this server); run this again after changing the DNS
# and it waits for the certificates.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
STATE=${SITE_STATE:-$HOME/.site}
WWW=www.facchini.eti.br
APEX=facchini.eti.br

KEY=$(tr -d '[:space:]' < ~/.dokploy-api-key)
api() {  # api <route> [json or @file]
  curl -fsS -m 60 -H "x-api-key: $KEY" -H "Content-Type: application/json" \
    ${2:+-X POST -d "$2"} "http://127.0.0.1:3000/api/$1"
}
json_file() {  # json_file <file> <python expression over env>: writes a JSON body to a file
  python3 -c "import json, os; json.dump($2, open('$1', 'w'))"
}
mkdir -p "$STATE"
chmod 700 "$STATE"

echo "== Dokploy: project Site, Compose site"
if [ -s "$STATE/compose-id" ]; then
  ID=$(cat "$STATE/compose-id")
  COMPOSE_FILE="$(cat "$HERE/compose.yml")" ID="$ID" \
    json_file /tmp/site-body.json '{"composeId": os.environ["ID"], "composeFile": os.environ["COMPOSE_FILE"]}'
  api compose.update @/tmp/site-body.json >/dev/null
  echo "   updated ($ID)"
else
  project=$(api project.all | python3 -c '
import json,sys
print(next((p["projectId"] for p in json.load(sys.stdin) if p["name"] == "Site"), ""))')
  if [ -z "$project" ]; then
    api project.create '{"name": "Site", "description": "www.facchini.eti.br"}' >/dev/null
    project=$(api project.all | python3 -c '
import json,sys
print(next(p["projectId"] for p in json.load(sys.stdin) if p["name"] == "Site"))')
  fi
  environment=$(api project.all | PROJECT="$project" python3 -c '
import json, os, sys
p = next(p for p in json.load(sys.stdin) if p["projectId"] == os.environ["PROJECT"])
print(p["environments"][0]["environmentId"])')
  COMPOSE_FILE="$(cat "$HERE/compose.yml")" ENVIRONMENT="$environment" \
    json_file /tmp/site-body.json '{"name": "site", "appName": "site", "environmentId": os.environ["ENVIRONMENT"], "composeType": "docker-compose", "sourceType": "raw", "composeFile": os.environ["COMPOSE_FILE"]}'
  ID=$(api compose.create @/tmp/site-body.json \
    | python3 -c 'import json,sys; print((json.load(sys.stdin) or {}).get("composeId", ""))' || true)
  if [ -z "$ID" ]; then  # the response may not carry it: look it up in the project
    ID=$(api project.all | PROJECT="$project" python3 -c '
import json, os, sys
p = next(p for p in json.load(sys.stdin) if p["projectId"] == os.environ["PROJECT"])
print(next(c["composeId"] for e in p["environments"] for c in e.get("compose", []) if c["name"] == "site"))')
  fi
  echo "$ID" > "$STATE/compose-id"
  echo "   created ($ID)"
fi
rm -f /tmp/site-body.json

# Compose does not recreate a container when only a "configs:" content changes: the fingerprint
# of compose.yml is a label of both services, so any change recreates them.
echo "== Settings (.env): the configuration fingerprint"
api "compose.one?composeId=$ID" | ID="$ID" HASH="$(sha256sum "$HERE/compose.yml" | cut -c1-12)" python3 -c '
import json, os, sys
env = (json.load(sys.stdin).get("env") or "").splitlines()
lines = [l for l in env if not l.startswith("CONFIG_HASH=")] + ["CONFIG_HASH=" + os.environ["HASH"]]
json.dump({"composeId": os.environ["ID"], "env": "\n".join(lines)}, open("/tmp/site-env.json", "w"))'
api compose.update @/tmp/site-env.json >/dev/null
rm -f /tmp/site-env.json
echo "   saved in Dokploy"

echo "== Deploy"
deployments() {  # "<count> <status of the newest>" of this Compose's deployments
  api "deployment.allByCompose?composeId=$ID" \
    | python3 -c 'import json,sys; d=json.load(sys.stdin); print(len(d), d[0]["status"] if d else "-")'
}
# Dokploy runs one deploy at a time: this one may wait behind another project's, so wait for a
# NEW deployment to show up and finish, not for the Compose's status (still the last one's).
before=$(deployments | cut -d' ' -f1)
api compose.deploy "{\"composeId\":\"$ID\",\"title\":\"setup.sh\"}" >/dev/null
for _ in $(seq 1 120); do
  read -r count newest < <(deployments)
  [ "$count" -gt "$before" ] && [ "$newest" != running ] && [ "$newest" != queued ] && break
  sleep 10
done
[ "$count" -gt "$before" ] && [ "$newest" = done ] || { echo "Dokploy's deploy: ${newest:-not started}" >&2; exit 1; }
APP=$(api "compose.one?composeId=$ID" | python3 -c 'import json,sys; print(json.load(sys.stdin)["appName"])')
container() {  # container <service>: the running container of that service
  sudo docker ps -q --filter "label=com.docker.compose.project=$APP" \
    --filter "label=com.docker.compose.service=$1" | head -1
}
echo "   done (Compose $APP)"

echo "== First build (builder: clone, pip install, construir.py)"
for _ in $(seq 1 60); do
  web=$(container web)
  [ -n "$web" ] && sudo docker exec "$web" test -f /srv/site/current/index.html && break
  sleep 5
done
sudo docker logs --tail 3 "$(container builder)" 2>&1 | sed 's/^/   /'
sudo docker exec "$(container web)" test -f /srv/site/current/index.html \
  || { echo "The site was not built: see the builder's log (docker logs $(container builder))" >&2; exit 1; }

echo "== Checks through Traefik, on this server (the certificate is not checked here)"
check() {  # check <expected code> <description> <curl arguments...>
  local expected=$1 what=$2 code
  shift 2
  code=$(curl -sk -m 20 -o /dev/null -w '%{http_code}' --resolve "$WWW:443:127.0.0.1" \
    --resolve "$APEX:443:127.0.0.1" --resolve "$WWW:80:127.0.0.1" --resolve "$APEX:80:127.0.0.1" "$@")
  printf '   %-46s %s %s\n' "$what" "$code" "$([ "$code" = "$expected" ] && echo ok || echo "EXPECTED $expected")"
}
check 200 "home page" "https://$WWW/"
check 200 "Kaladrius's page" "https://$WWW/kaladrius/"
check 200 "sitemap.xml" "https://$WWW/sitemap.xml"
check 301 "folder without the final /" "https://$WWW/sobre"
check 301 "facchini.eti.br goes to www" "https://$APEX/kaladrius/"
location=$(curl -sk -m 20 -o /dev/null -w '%{redirect_url}' --resolve "$APEX:443:127.0.0.1" "https://$APEX/kaladrius/")
printf '   %-46s %s %s\n' "   to" "$location" "$([ "$location" = "https://$WWW/kaladrius/" ] && echo ok || echo "EXPECTED https://$WWW/kaladrius/")"
# Dokploy's Traefik redirects every http request itself (301) before the site's router.
check 301 "http goes to https" "http://$WWW/"

echo "== DNS and certificates"
here=" $(hostname -I) "
valid() {  # valid <host>: Traefik here serves a certificate curl trusts for it
  curl -sS -m 10 -o /dev/null --resolve "$1:443:127.0.0.1" "https://$1/" 2>/dev/null
}
pending=""
# Asked to the domain's own name servers, as Let's Encrypt does: this server's resolver may keep
# the old address for up to the records' TTL (an hour).
nameserver=$(dig +short NS "$APEX" | head -1)
for host in "$WWW" "$APEX"; do
  points=$(dig +short A "$host" @"${nameserver:-a.sec.dns.br}" | tail -1)
  if valid "$host"; then
    printf '   %-24s DNS %-16s certificate ok\n' "$host" "$points"
  elif [[ "$here" == *" $points "* ]]; then
    pending="$pending $host"
    printf '   %-24s DNS %-16s points here, certificate pending\n' "$host" "$points"
  else
    printf '   %-24s DNS %-16s NOT here yet: change it at Registro.br, then run this again\n' "$host" "$points"
  fi
done
if [ -n "$pending" ]; then
  # Traefik asks Let's Encrypt again when the site's routers come back.
  echo "   restarting the site's nginx so Traefik asks Let's Encrypt for:$pending"
  sudo docker restart "$(container web)" >/dev/null
  for host in $pending; do
    for _ in $(seq 1 36); do valid "$host" && break; sleep 5; done
    if valid "$host"; then
      printf '   %-24s certificate ok\n' "$host"
    else
      printf '   %-24s certificate still missing: see docker logs dokploy-traefik\n' "$host"
    fi
  done
fi
echo "Done: https://$WWW"
