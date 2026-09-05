#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

test "$(id -un)" = vscode
test "$(node --version)" = v22.22.2
npm --version
yarn --version
pnpm --version
swa --version
npm ls -g --depth=0
# Load SWA's native credential dependency without accessing a keyring.
node -e 'require(process.argv[1])' "$(npm root -g)/@azure/static-web-apps-cli/node_modules/keytar"
oh-my-posh version
bash -ic 'test "$(type -t nvm)" = function && nvm current'
zsh -ic 'command -v node'
gh --version
az version
bicep --version
az bicep version
dotnet --list-sdks
dotnet --list-runtimes | grep -E '^Microsoft.NETCore.App 8\.'
func --version
for tool in git sudo zsh python3 make gcc g++ dig ip ping mtr nc nmap rg tcpdump traceroute wget whois; do
    command -v "$tool"
done
test -w /commandhistory
test -w /home/vscode/.codex
test -w "$NVM_DIR"
core_tools_dir="$(dirname "$(readlink -f "$(command -v func)")")"
test -s "$core_tools_dir/workers/powershell/7.6/Microsoft.Azure.Functions.PowerShellWorker.dll"
test ! -d /usr/share/dotnet/sdk/3.1.426
test ! -d /tmp/worker
sudo -n test ! -d /root/.nuget
test ! -d "$NVM_DIR/.cache"
apt_cache_files="$(sudo -n find /var/lib/apt/lists /var/cache/apt/archives -type f ! -name lock -print -quit)"
test -z "$apt_cache_files"
test -z "$(find /opt/az -type d -name __pycache__ -print -quit)"
pwsh -NoLogo -NoProfile -File "$repo_root/.devcontainer/test-image.ps1"
pwsh -NoLogo -Command 'if ((Get-PSReadLineOption).HistorySavePath -ne "/commandhistory/ConsoleHost_history.txt") { throw "History profile was not loaded" }'

# Exercise the actual 7.6 Functions worker through an HTTP trigger, without
# credentials, Azurite, managed dependencies or an extension-bundle download.
app_dir="$(mktemp -d)"
host_pid=''
trap 'if [[ -n "$host_pid" ]]; then kill "$host_pid" 2>/dev/null || true; wait "$host_pid" 2>/dev/null || true; fi; rm -rf "$app_dir"' EXIT
mkdir -p "$app_dir/HelloWorld"
cp "$repo_root"/examples/powershell-7.6.5/function/HelloWorld/{run.ps1,function.json} "$app_dir/HelloWorld/"
printf '%s\n' '{"version":"2.0","managedDependency":{"enabled":false}}' > "$app_dir/host.json"
cd "$app_dir"
FUNCTIONS_WORKER_RUNTIME=powershell FUNCTIONS_WORKER_RUNTIME_VERSION=7.6 \
    func start --port 7079 > "$app_dir/host.log" 2>&1 &
host_pid=$!
for attempt in {1..90}; do
    if curl --silent --fail --max-time 2 'http://localhost:7079/api/HelloWorld?name=SmokeTest' > "$app_dir/response"; then
        grep -F 'Hello, SmokeTest.' "$app_dir/response"
        echo 'Image smoke tests passed.'
        exit 0
    fi
    if ! kill -0 "$host_pid" 2>/dev/null; then break; fi
    sleep 1
done
cat "$app_dir/host.log"
exit 1
