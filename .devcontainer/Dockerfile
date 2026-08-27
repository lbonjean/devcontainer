FROM mcr.microsoft.com/vscode/devcontainers/base:ubuntu-24.04

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y --no-install-recommends \
        curl \
        dnsutils \
        iproute2 \
        iputils-ping \
        mtr-tiny \
        net-tools \
        netcat-openbsd \
        nmap \
        ripgrep \
        tcpdump \
        traceroute \
        wget \
        whois \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN install -d -o vscode -g vscode \
        /commandhistory \
        /home/vscode/.config/powershell \
    && printf '%s\n' '. /home/vscode/.config/powershell/pwshsettings.ps1' \
        > /home/vscode/.config/powershell/Microsoft.PowerShell_profile.ps1 \
    && chown vscode:vscode \
        /home/vscode/.config/powershell/Microsoft.PowerShell_profile.ps1

COPY --chown=vscode:vscode .devcontainer/pwshsettings.ps1 \
    /home/vscode/.config/powershell/pwshsettings.ps1
