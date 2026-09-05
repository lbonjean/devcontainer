# syntax=docker/dockerfile:1
FROM ubuntu:26.04 AS tools

USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG POWERSHELL_VERSION=7.6.5
ARG NODE_VERSION=22.22.2
ARG NVM_VERSION=0.40.3
ARG DOTNET_CHANNEL=LTS
ARG DOTNET_RUNTIME_CHANNEL=8.0

ENV DOTNET_ROOT=/usr/share/dotnet \
    DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1 \
    NVM_DIR=/usr/local/share/nvm \
    NVM_SYMLINK_CURRENT=true \
    PATH=/usr/local/share/nvm/current/bin:/usr/share/dotnet:/home/vscode/.dotnet/tools:${PATH}

# Supply the development utilities explicitly when using the official Ubuntu base.
# Keep compilers/Python: nodeGypDependencies was enabled in the Node feature.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bubblewrap ca-certificates curl dnsutils g++ git gnupg iproute2 iputils-ping \
        libicu78 libssl3t64 libunwind8 locales make mtr-tiny net-tools netcat-openbsd \
        nmap openssh-client procps python3-minimal ripgrep sudo tcpdump traceroute unzip wget whois xz-utils zsh \
    && install -d -m 0755 /etc/apt/keyrings \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor --yes -o /etc/apt/keyrings/microsoft.gpg \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        -o /etc/apt/keyrings/githubcli.gpg \
    && chmod 0644 /etc/apt/keyrings/*.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/azure-cli/ resolute main" \
        > /etc/apt/sources.list.d/azure-cli.list \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update \
    && curl -fsSL "https://github.com/PowerShell/PowerShell/releases/download/v${POWERSHELL_VERSION}/powershell_${POWERSHELL_VERSION}-1.deb_amd64.deb" \
        -o /tmp/powershell.deb \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        azure-cli gh /tmp/powershell.deb \
    && find /opt/az -type d -name __pycache__ -prune -exec rm -rf '{}' + \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Ubuntu supplies UID/GID 1000 as ubuntu; preserve the IDs for bind mounts.
RUN if id ubuntu >/dev/null 2>&1; then \
        usermod --login vscode --home /home/vscode --move-home ubuntu; \
        groupmod --new-name vscode ubuntu; \
    elif ! id vscode >/dev/null 2>&1; then \
        groupadd --gid 1000 vscode; \
        useradd --uid 1000 --gid vscode --create-home --shell /bin/bash vscode; \
    fi \
    && usermod --shell /bin/bash --append --groups sudo vscode \
    && printf '%s\n' 'vscode ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode \
    && visudo --check \
    && locale-gen en_US.UTF-8 \
    && chown -R vscode:vscode /home/vscode

ENV LANG=en_US.UTF-8

# Install into the same location used by the .NET feature and worker bootstrap.
# Archives and installer scripts are deleted before this layer is committed.
RUN curl -fsSL https://dot.net/v1/dotnet-install.sh -o /tmp/dotnet-install.sh \
    && bash /tmp/dotnet-install.sh --channel "$DOTNET_CHANNEL" --install-dir "$DOTNET_ROOT" --no-path \
    && bash /tmp/dotnet-install.sh --channel "$DOTNET_RUNTIME_CHANNEL" --runtime dotnet --install-dir "$DOTNET_ROOT" --no-path \
    && ln -sf "$DOTNET_ROOT/dotnet" /usr/local/bin/dotnet \
    && rm -rf /tmp/* /root/.dotnet /root/.nuget /root/.cache

# Retain nvm, npm, Yarn and pnpm from the Node feature, including user writes.
# Bootstrap npm outside its global prefix: replacing the running npm 10 can
# remove modules it still needs during installation cleanup.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends libsecret-1-dev pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && install -d -o vscode -g vscode "$NVM_DIR" \
    && curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/v${NVM_VERSION}/install.sh" -o /tmp/install-nvm.sh \
    && runuser -u vscode -- env PROFILE=/dev/null METHOD=script bash /tmp/install-nvm.sh \
    && runuser -u vscode -- bash -c 'set -e; source "$NVM_DIR/nvm.sh"; nvm install "$1" && nvm alias default "$1" && npm install --prefix /tmp/npm-bootstrap npm@latest && node /tmp/npm-bootstrap/node_modules/npm/bin/npm-cli.js install -g npm@latest && npm install -g --allow-scripts=yarn,keytar yarn@latest pnpm@latest @azure/static-web-apps-cli@latest && npm update -g --allow-scripts=yarn,keytar' -- "$NODE_VERSION" \
    && printf '%s\n' 'export NVM_DIR=/usr/local/share/nvm' \
        '[ ! -s "$NVM_DIR/nvm.sh" ] || . "$NVM_DIR/nvm.sh"' > /etc/profile.d/nvm.sh \
    && printf '\n%s\n' '. /etc/profile.d/nvm.sh' >> /etc/bash.bashrc \
    && printf '\n%s\n' '. /etc/profile.d/nvm.sh' >> /etc/zsh/zshrc \
    && rm -rf "$NVM_DIR/.cache" /home/vscode/.npm /home/vscode/.cache /tmp/*

# Install the standalone prompt engine for all users (not the retired PS module).
RUN curl -fsSL https://ohmyposh.dev/install.sh -o /tmp/install-oh-my-posh.sh \
    && bash /tmp/install-oh-my-posh.sh -d /usr/local/bin \
    && oh-my-posh version \
    && rm -rf /tmp/* /root/.cache

# A global Bicep binary avoids a second user-specific download via az bicep.
RUN arch="$(dpkg --print-architecture)" \
    && case "$arch" in amd64) bicep_arch=x64 ;; arm64) bicep_arch=arm64 ;; *) exit 1 ;; esac \
    && curl -fsSL "https://github.com/Azure/bicep/releases/latest/download/bicep-linux-${bicep_arch}" -o /usr/local/bin/bicep \
    && chmod 0755 /usr/local/bin/bicep \
    && runuser -u vscode -- az config set bicep.use_binary_from_path=true \
    && find /home/vscode/.azure -mindepth 1 -maxdepth 1 ! -name config -exec rm -rf '{}' + \
    && rm -rf /home/vscode/.cache /tmp/*

FROM tools AS worker-build
ARG WORKER_VERSION=4.0.5362

# The legacy SDK used for packaging, build modules, sources and NuGet caches
# exist only in this stage. Only the published worker is consumed below.
RUN test "$(dpkg --print-architecture)" = amd64 \
    && mkdir -p /tmp/worker \
    && curl -fsSL "https://github.com/Azure/azure-functions-powershell-worker/archive/refs/tags/v${WORKER_VERSION}.tar.gz" \
        | tar -xz --strip-components=1 -C /tmp/worker \
    && cd /tmp/worker \
    && pwsh -NoLogo -NoProfile -Command '$ErrorActionPreference = "Stop"; $PSNativeCommandUseErrorActionPreference = $true; ./build.ps1 -Bootstrap -Configuration Release' \
    && test -s src/bin/Release/net10.0/publish/Microsoft.Azure.Functions.PowerShellWorker.dll \
    && mkdir /worker-output \
    && cp -a src/bin/Release/net10.0/publish/. /worker-output/

FROM tools AS final
ARG CORE_TOOLS_VERSION=4.14.0

# Use a build-stage mount so even a bundled 7.6 worker is replaced in the
# installation layer, without retaining the original copy in an earlier layer.
RUN --mount=type=bind,from=worker-build,source=/worker-output,target=/mnt/worker,ro \
    curl -fsSL "https://github.com/Azure/azure-functions-core-tools/releases/download/${CORE_TOOLS_VERSION}/Azure.Functions.Cli.linux-x64.${CORE_TOOLS_VERSION}.zip" \
        -o /tmp/core-tools.zip \
    && mkdir -p /usr/lib/azure-functions-core-tools-4 \
    && unzip -q /tmp/core-tools.zip -d /usr/lib/azure-functions-core-tools-4 \
    && chmod 0755 /usr/lib/azure-functions-core-tools-4/func \
    && ln -sf /usr/lib/azure-functions-core-tools-4/func /usr/local/bin/func \
    && core_tools_dir="$(dirname "$(readlink -f "$(command -v func)")")" \
    && test -s "$core_tools_dir/workers/powershell/worker.config.json" \
    && rm -rf "$core_tools_dir/workers/powershell/7.6" \
    && mkdir -p "$core_tools_dir/workers/powershell/7.6" \
    && cp -a /mnt/worker/. "$core_tools_dir/workers/powershell/7.6/" \
    && chmod -R a+rX "$core_tools_dir/workers/powershell/7.6" \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Stage modules outside PSModulePath to avoid updating a module already loaded
# by PowerShellGet while resolving dependencies. Retain CurrentUser scope.
RUN runuser -u vscode -- pwsh -NoLogo -NoProfile -Command \
        '$ErrorActionPreference = "Stop"; $staging = New-Item -ItemType Directory -Path /tmp/powershell-modules -Force; Save-Module -Name PowerShellGet, PSReadLine, Az.Accounts, Microsoft.Graph.Authentication, PnP.PowerShell, Pester, ExchangeOnlineManagement -Path $staging.FullName -Force; $destination = New-Item -ItemType Directory -Path "$HOME/.local/share/powershell/Modules" -Force; Copy-Item "$staging/*" $destination.FullName -Recurse -Force' \
    && rm -rf /home/vscode/.cache /home/vscode/.local/share/powershell/PowerShellGet \
        /root/.cache /tmp/* /var/tmp/*

RUN install -d -o vscode -g vscode \
        /commandhistory /home/vscode/.codex /home/vscode/.config/powershell \
    && printf '%s\n' '. /home/vscode/.config/powershell/pwshsettings.ps1' \
        > /home/vscode/.config/powershell/Microsoft.PowerShell_profile.ps1 \
    && chown vscode:vscode /home/vscode/.config/powershell/Microsoft.PowerShell_profile.ps1

COPY --chown=vscode:vscode .devcontainer/pwshsettings.ps1 \
    /home/vscode/.config/powershell/pwshsettings.ps1
