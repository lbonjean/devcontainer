# syntax=docker/dockerfile:1

FROM ubuntu:26.04 AS tools

USER root

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG POWERSHELL_VERSION=7.6.10




ENV DOTNET_CLI_TELEMETRY_OPTOUT=1 \
    DOTNET_NOLOGO=1 \
    NPM_CONFIG_PREFIX=/usr/local/share/npm-global \
    PATH=/usr/local/share/npm-global/bin:/home/vscode/.dotnet/tools:${PATH}

# Retain documentation for existing and future packages, and restore the content
# stripped from the Ubuntu base. man-db replaces Ubuntu's placeholder man script.
RUN rm -f /etc/dpkg/dpkg.cfg.d/excludes \
    && if [ "$(dpkg-divert --truename /usr/bin/man)" = /usr/bin/man.REAL ]; then \
        rm -f /usr/bin/man; \
        dpkg-divert --quiet --rename --remove /usr/bin/man; \
    fi \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends --reinstall \
        $(dpkg-query -W -f='${binary:Package}\n') \
        man-db manpages manpages-dev less info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Supply the development utilities explicitly when using the official Ubuntu base.
# Keep compilers/Python: nodeGypDependencies was enabled in the Node feature.
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        bubblewrap \
        ca-certificates \
        curl \
        dnsutils \
        fonts-freefont-ttf \
        fonts-ipafont-gothic \
        fonts-liberation \
        fonts-noto-color-emoji \
        fonts-tlwg-loma-otf \
        fonts-unifont \
        fonts-wqy-zenhei \
        g++ \
        git \
        gnupg \
        iproute2 \
        iputils-ping \
        libasound2t64 \
        libatk-bridge2.0-0t64 \
        libatk1.0-0t64 \
        libatspi2.0-0t64 \
        libcairo2 \
        libcups2t64 \
        libdbus-1-3 \
        libdrm2 \
        libfontconfig1 \
        libfreetype6 \
        libgbm1 \
        libglib2.0-0t64 \
        libicu78 \
        libnspr4 \
        libnss3 \
        libpango-1.0-0 \
        libssl3t64 \
        libunwind8 \
        libwayland-client0 \
        libx11-6 \
        libxcb1 \
        libxcomposite1 \
        libxdamage1 \
        libxext6 \
        libxfixes3 \
        libxkbcommon0 \
        libxrandr2 \
        locales \
        make \
        mtr-tiny \
        net-tools \
        netcat-openbsd \
        nmap \
        nodejs \
        npm \
        software-properties-common \
        openssh-client \
        procps \
        python3-minimal \
        python3-pip \
        python3-yaml \
        python3-venv \
        ripgrep \
        sudo \
        tcpdump \
        tmux \
        traceroute \
        unzip \
        wget \
        whois \
        xdg-utils \
        xfonts-cyrillic \
        xfonts-scalable \
        xz-utils \
        zsh \
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

# Ubuntu supplies the SDK; its .NET backports feed supplies the retained runtime.
RUN add-apt-repository --yes ppa:dotnet/backports \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        dotnet-sdk-10.0 dotnet-runtime-8.0 libsecret-1-dev pkg-config \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Keep Ubuntu's Node.js and npm. Global developer tools remain writable by vscode.
RUN install -d -o vscode -g vscode "$NPM_CONFIG_PREFIX" \
    && runuser -u vscode -- npm install -g --engine-strict yarn pnpm @azure/static-web-apps-cli \
    && rm -rf /home/vscode/.npm /home/vscode/.cache /tmp/*

# A global Bicep binary avoids a second user-specific download via az bicep.
RUN arch="$(dpkg --print-architecture)" \
    && case "$arch" in amd64) bicep_arch=x64 ;; arm64) bicep_arch=arm64 ;; *) exit 1 ;; esac \
    && curl -fsSL "https://github.com/Azure/bicep/releases/latest/download/bicep-linux-${bicep_arch}" -o /usr/local/bin/bicep \
    && chmod 0755 /usr/local/bin/bicep \
    && runuser -u vscode -- az config set bicep.use_binary_from_path=true \
    && find /home/vscode/.azure -mindepth 1 -maxdepth 1 ! -name config -exec rm -rf '{}' + \
    && rm -rf /home/vscode/.cache /tmp/*

# FROM tools AS worker-build

# ARG WORKER_VERSION=4.0.5362

# # The legacy SDK used for packaging, build modules, sources and NuGet caches
# # exist only in this stage. Only the published worker is consumed below.
# RUN test "$(dpkg --print-architecture)" = amd64 \
#     && mkdir -p /tmp/worker \
#     && curl -fsSL "https://github.com/Azure/azure-functions-powershell-worker/archive/refs/tags/v${WORKER_VERSION}.tar.gz" \
#         | tar -xz --strip-components=1 -C /tmp/worker \
#     && cd /tmp/worker \
#     && pwsh -NoLogo -NoProfile -Command '$ErrorActionPreference = "Stop"; $PSNativeCommandUseErrorActionPreference = $true; ./build.ps1 -Bootstrap -Configuration Release' \
#     && test -s src/bin/Release/net10.0/publish/Microsoft.Azure.Functions.PowerShellWorker.dll \
#     && mkdir /worker-output \
#     && cp -a src/bin/Release/net10.0/publish/. /worker-output/

FROM tools AS final
ARG CORE_TOOLS_VERSION=4.16.0

RUN curl -fsSL \
      "https://github.com/Azure/azure-functions-core-tools/releases/download/${CORE_TOOLS_VERSION}/Azure.Functions.Cli.linux-x64.${CORE_TOOLS_VERSION}.zip" \
      -o /tmp/core-tools.zip \
    && mkdir -p /usr/lib/azure-functions-core-tools-4 \
    && unzip -q /tmp/core-tools.zip -d /usr/lib/azure-functions-core-tools-4 \
    && chmod 0755 /usr/lib/azure-functions-core-tools-4/func \
    && ln -sf /usr/lib/azure-functions-core-tools-4/func /usr/local/bin/func \
    && rm -f /tmp/core-tools.zip
# Use a build-stage mount so even a bundled 7.6 worker is replaced in the
# installation layer, without retaining the original copy in an earlier layer.
# RUN --mount=type=bind,from=worker-build,source=/worker-output,target=/mnt/worker,ro \
#     curl -fsSL "https://github.com/Azure/azure-functions-core-tools/releases/download/${CORE_TOOLS_VERSION}/Azure.Functions.Cli.linux-x64.${CORE_TOOLS_VERSION}.zip" \
#         -o /tmp/core-tools.zip \
#     && mkdir -p /usr/lib/azure-functions-core-tools-4 \
#     && unzip -q /tmp/core-tools.zip -d /usr/lib/azure-functions-core-tools-4 \
#     && chmod 0755 /usr/lib/azure-functions-core-tools-4/func \
#     && ln -sf /usr/lib/azure-functions-core-tools-4/func /usr/local/bin/func \
#     && core_tools_dir="$(dirname "$(readlink -f "$(command -v func)")")" \
#     && test -s "$core_tools_dir/workers/powershell/worker.config.json" \
#     && rm -rf "$core_tools_dir/workers/powershell/7.6" \
#     && mkdir -p "$core_tools_dir/workers/powershell/7.6" \
#     && cp -a /mnt/worker/. "$core_tools_dir/workers/powershell/7.6/" \
#     && chmod -R a+rX "$core_tools_dir/workers/powershell/7.6" \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Stage modules outside PSModulePath to avoid updating a module already loaded
# by PowerShellGet while resolving dependencies. Retain CurrentUser scope.
# RUN runuser -u vscode -- pwsh -NoLogo -NoProfile -Command \
#         '$ErrorActionPreference = "Stop"; $staging = New-Item -ItemType Directory -Path /tmp/powershell-modules -Force; Save-Module -Name PowerShellGet, PSReadLine, Az, Microsoft.Graph, PnP.PowerShell, Pester, ExchangeOnlineManagement -Path $staging.FullName -Force; $destination = New-Item -ItemType Directory -Path "/usr/local/share/powershell/Modules" -Force; Copy-Item "$staging/*" $destination.FullName -Recurse -Force' \
#     && rm -rf /home/vscode/.cache /home/vscode/.local/share/powershell/PowerShellGet \
#         /root/.cache /tmp/* /var/tmp/*

# Install PowerShell modules system-wide
RUN pwsh -NoLogo -NoProfile -Command \
    '$ErrorActionPreference = "Stop"; \
     $staging = "/tmp/powershell-modules"; \
     New-Item -ItemType Directory -Path $staging -Force | Out-Null; \
     Save-Module -Name PowerShellGet, PSReadLine, Az, Microsoft.Graph, PnP.PowerShell, Pester, ExchangeOnlineManagement -Path $staging -Force; \
     $destination = "/usr/local/share/powershell/Modules"; \
     New-Item -ItemType Directory -Path $destination -Force | Out-Null; \
     Copy-Item "$staging/*" $destination -Recurse -Force' \
    && rm -rf /tmp/powershell-modules /root/.cache /tmp/*



RUN install -d -o vscode -g vscode \
        /home/vscode /home/vscode/.codex /commandhistory
#        /commandhistory /home/vscode/.codex /home/vscode/.config/powershell /home/vscode/.copilot /home/vscode/.claude /persistent
    #&& printf '%s\n' '. /home/vscode/.config/powershell/pwshsettings.ps1' \
    #    > /home/vscode/.config/powershell/Microsoft.PowerShell_profile.ps1 \
    # && chown vscode:vscode /home/vscode/.config/powershell/Microsoft.PowerShell_profile.ps1

COPY --chown=vscode:vscode .devcontainer/pwshsettings.ps1 \
    /home/vscode/.config/powershell/pwshsettings.ps1
