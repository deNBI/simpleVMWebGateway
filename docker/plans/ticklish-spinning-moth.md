# Implementation Plan: IP Blocklist Automation

## Context
The goal is to automate the update of IP blocklists in the OpenResty gateway. Currently, `generate_ip_blocklists.sh` exists but is not integrated into the container's lifecycle. We need to ensure these lists are updated every two hours and that OpenResty reloads its configuration to apply the new blocks.

## Proposed Changes

### 1. Dockerfile Updates
- Update the `apt-get install` list to include `cron` and `curl`.
- Copy `generate_ip_blocklists.sh` and `ip_blocklists.txt` to `/opt/scripts/`.
- Ensure `generate_ip_blocklists.sh` has executable permissions.
- Create a cron job file in `/etc/cron.d/ip-blocklist` with the following schedule:
  `0 */2 * * * root /opt/scripts/generate_ip_blocklists.sh && /usr/sbin/openresty -s reload`

### 2. Launch Script Updates
- Modify `launch.sh` to start the `cron` daemon before starting OpenResty and FastAPI.

### 3. File Renaming
- `ip_blocklists.sh` has already been renamed to `ip_blocklists.txt` to reflect its content as a list of URLs.

## Critical Files
- `/home/ubuntu/workspace/denbi/simpleVMWebGateway/docker/Dockerfile`
- `/home/ubuntu/workspace/denbi/simpleVMWebGateway/docker/launch.sh`
- `/home/ubuntu/workspace/denbi/simpleVMWebGateway/docker/generate_ip_blocklists.sh`
- `/home/ubuntu/workspace/denbi/simpleVMWebGateway/docker/ip_blocklists.txt`

## Verification Plan
1. Build the docker image.
2. Run the container.
3. Manually execute `/opt/scripts/generate_ip_blocklists.sh` and verify that `/etc/openresty/block_ips_geo.conf` is populated.
4. Verify that `cron` is running inside the container (`ps aux | grep cron`).
5. (Optional) Temporarily change the cron schedule to every minute to verify the automatic update and reload.
