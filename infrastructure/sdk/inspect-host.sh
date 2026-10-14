#!/usr/bin/env bash
# Read-only host inventory. No installations, container changes or key/config reads.
set -u

run_check() {
    printf '\n%s\n' "$1"
    shift
    "$@" || printf 'Check unavailable (exit %s); recorded as unknown.\n' "$?"
}

run_check 'LXD pool capacity' lxc storage info pool
run_check 'LXD pool settings (storage only)' lxc storage show pool
run_check 'Existing profile names' lxc profile list
run_check 'Bridge addresses' ip -brief address show br0
run_check 'Volume group allocation (sudo read-only query)' sudo vgs --units g -o vg_name,vg_size,vg_free
run_check 'Logical volume / thin-pool utilization (sudo read-only query)' sudo lvs --units g -o vg_name,lv_name,lv_size,segtype,pool_lv,data_percent,metadata_percent

printf '\nInventory complete. No install or configuration changes performed.\n'
