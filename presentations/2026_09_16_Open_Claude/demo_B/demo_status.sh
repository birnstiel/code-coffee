#!/bin/bash
# demo_status.sh — read-only Slurm queue status, over ssh.
# Cannot change cluster state: squeue only, never sbatch/scancel/scontrol.
#   ./demo_status.sh
set -uo pipefail

HOST="cluster.hpc.physik.uni-muenchen.de"
RUSER="ch.lau"
FMT='%i|%j|%T|%r|%R'

# BatchMode=yes  — never stop to ask for a password or passphrase.
# ConnectTimeout applies per *resolved address*, so a dual-stack host can hang
# well past it when the VPN is down; timeout caps the whole call instead.
Q=$(timeout 25 ssh -o BatchMode=yes -o ConnectTimeout=10 \
        "$RUSER@$HOST" "/opt/slurm/bin/squeue -u $RUSER -r -h -o '$FMT'") || {
    rc=$?
    (( rc == 124 )) \
        && echo "cannot reach $HOST: timed out after 25s" \
        || echo "ssh to $HOST failed (rc $rc)"
    echo "  VPN down? check with:  ./demo_connect.sh status"
    exit 1
}

printf '%s  queue status\n' "$(date '+%F %T')"
printf '  %-10s %s\n' RUNNING "$(grep -c '|RUNNING|' <<<"$Q")" \
                      PENDING "$(grep -c '|PENDING|' <<<"$Q")"
echo "  pending reasons:"
awk -F'|' '$3=="PENDING"{print $4}' <<<"$Q" | sort | uniq -c | sed 's/^/    /'
echo "  jobs by name:"
awk -F'|' '{print $2}' <<<"$Q" | sort | uniq -c | sed 's/^/    /'
# the only line that ever needs changing when you want an alert:
n_run=$(grep -c '|RUNNING|' <<<"$Q")
(( n_run == 0 )) && echo "  !! nothing running — check the campaign"
exit 0
