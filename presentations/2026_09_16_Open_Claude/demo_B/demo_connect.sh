#!/bin/bash
# demo_connect.sh — the mutating counterpart to demo_status.sh.
# Brings the LMU WireGuard tunnel up or down, and nothing else.
#
#   ./demo_connect.sh status           # read-only: is the tunnel up?
#   ./demo_connect.sh up   [--dry-run]
#   ./demo_connect.sh down [--dry-run]
#
# Needs three narrowly scoped NOPASSWD rules (verify with `sudo -l`):
#   /usr/bin/wg-quick up lmu-vpn, /usr/bin/wg-quick down lmu-vpn, /usr/bin/wg show
#
# NOTE: sudoers matches arguments *exactly*, so the rule `/usr/bin/wg show`
# permits only the bare command — `sudo wg show lmu-vpn` is refused. Hence the
# interface is filtered out of the output here rather than passed as an argument.
set -uo pipefail

IFACE="lmu-vpn"
TRIES=10                 # wg-quick up returns immediately; the handshake is async
ACTION="${1:-status}"
DRY=0
[[ "${2:-}" == "--dry-run" ]] && DRY=1

run()   { if (( DRY )); then echo "DRY-RUN: $*"; else "$@"; fi; }

# true if the interface exists at all (wg-quick up succeeded)
iface_exists() { sudo -n wg show 2>/dev/null | grep -q "^interface: $IFACE$"; }

# true if $IFACE exists and has completed a handshake
is_up() {
    sudo -n wg show 2>/dev/null | awk -v want="$IFACE" '
        /^interface:/      { cur = $2 }
        /latest handshake:/{ if (cur == want) ok = 1 }
        END                { exit !ok }'
}

# -n never prompts, so a missing sudo rule fails loudly instead of hanging
preflight() {
    sudo -n wg show >/dev/null 2>&1 && return 0
    echo "cannot run 'sudo wg show' without a password prompt."
    echo "add the rules with:  sudo visudo -f /etc/sudoers.d/wg-lmu"
    exit 2
}

case "$ACTION" in
    status)
        preflight
        if is_up; then
            echo "$IFACE: up"
            # Only the four lines that matter. A sed range to the next blank
            # line would stop before `peer:` and hide the handshake; the keys
            # and the allowed-ips list are noise, and not for slides.
            sudo -n wg show 2>/dev/null | awk -v want="$IFACE" '
                /^interface:/                                { p = ($2 == want); if (p) print }
                p && /endpoint:|latest handshake:|transfer:/  { print }'
        else
            echo "$IFACE: down"
        fi
        ;;
    up)
        preflight
        is_up && { echo "$IFACE: already up"; exit 0; }
        if (( DRY )); then
            echo "DRY-RUN: sudo -n wg-quick down $IFACE   # kill first, clears a one-sided tunnel"
            echo "DRY-RUN: sudo -n wg-quick up   $IFACE"
            echo "DRY-RUN: sleep 1, then look for a handshake; repeat up to $TRIES times"
            exit 0
        fi
        # A tunnel can come up one-sided: the interface exists and traffic is
        # being sent, but the peer never answers, so there is no handshake.
        # Tearing it down and re-dialling is what actually clears that.
        for (( i = 1; i <= TRIES; i++ )); do
            sudo -n wg-quick down "$IFACE" >/dev/null 2>&1
            sudo -n wg-quick up   "$IFACE" >/dev/null 2>&1
            sleep 1
            if is_up; then
                echo "$IFACE: up (attempt $i/$TRIES)"
                exit 0
            fi
            if iface_exists; then
                echo "$IFACE: interface up, no handshake — one-sided, re-dialling ($i/$TRIES)"
            else
                echo "$IFACE: wg-quick up did not create the interface ($i/$TRIES)"
            fi
        done
        # do not leave a one-sided tunnel behind: it installs routes that then
        # black-hole cluster traffic instead of failing cleanly
        sudo -n wg-quick down "$IFACE" >/dev/null 2>&1
        echo "$IFACE: no handshake after $TRIES attempts — gave up, interface torn down"
        exit 1
        ;;
    down)
        preflight
        run sudo -n wg-quick down "$IFACE"
        (( DRY )) || echo "$IFACE: down"
        ;;
    *)
        echo "usage: $(basename "$0") {status|up|down} [--dry-run]"
        exit 64
        ;;
esac
