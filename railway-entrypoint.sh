#!/usr/bin/env bash
set -euo pipefail
# Railway mounts one persistent volume. Keep secrets inaccessible to agent UID.
if [[ -L /persist || ! -d /persist ]]; then
  echo "Persistent volume /persist missing" >&2
  exit 1
fi
chown root:root /persist
chmod 0711 /persist
install -d -m 0755 -o root -g root /persist/data
install -d -m 0700 -o root -g root /persist/config
# The original upstream tools use hardcoded /data and /config paths.
for name in data config; do
  if [[ -L /${name} ]]; then
    test "$(readlink /${name})" = "/persist/${name}"
  else
    # Only replace empty image directories, never erase mounted/user data.
    if [[ "$name" == data ]]; then
      for sub in generated chats output; do
        if [[ -d /data/$sub ]]; then rmdir /data/$sub; fi
      done
    fi
    rmdir "/${name}"
    ln -s "/persist/${name}" "/${name}"
  fi
done
export DISPLAY="${DISPLAY:-:99}"
display_num="${DISPLAY#:}"
rm -f "/tmp/.X${display_num}-lock" "/tmp/.X11-unix/X${display_num}"
Xvfb "$DISPLAY" -screen 0 1920x1080x24 &
xvfb_pid=$!
for _ in $(seq 1 100); do
  if xdpyinfo -display "$DISPLAY" >/dev/null 2>&1; then break; fi
  kill -0 "$xvfb_pid"
  sleep 0.1
done
xdpyinfo -display "$DISPLAY" >/dev/null
# Railway terminates HTTPS. Do not start the LAN TLS or localhost OAuth relays.
exec "$@"
