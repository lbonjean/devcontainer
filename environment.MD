# Environment configuration

A properly configured environment is important and makes your live easier. Especially if using several identities.
To separate all these identities I use 'firefox in private', but you can use whatever browser you want.

Variables:

- BROWSER: used by az,gh,
- GH_BROWSER: Overrides BROWSER (if specified) for GH

If you do not set these variables, your default browser will be used, all the accounts will end up in your profile.

## CMD

Do this once for your user account in a CMD prompt local on your machine.  
It will set some environment variables and creates a browser helper file.  
The example uses firefox, you can use whatever browser you want.

```text
setx GH_BROWSER "C:/users/c0000-luc/.config/mysettings/firefox.cmd"
setx BROWSER "\"C:/Program Files/Mozilla Firefox/firefox.exe\" -private-window %s"

mkdir "%USERPROFILE%\.config\mysettings" 2>nul
(
echo @echo off
echo start "" "C:\Program Files\Mozilla Firefox\firefox.exe" -private-window "%*"
) > "%USERPROFILE%\.config\mysettings\firefox.cmd"

more "%USERPROFILE%\.config\mysettings\firefox.cmd"

```

## Powershell

Powershell inherits/shares the enviroment with CMD.

## WSL / Linux

### In .bashrc

```text
export BROWSER="$HOME/bin/firefox-private"
eval $($HOME/wsl2-ssh-agent)
```
[wsl2-ssh-agent](https://github.com/mame/wsl2-ssh-agent): Tool to forward ssh agent from windows to wsl, so that it also gets forwarded into devcontainers if started with code .


### In $HOME/bin/firefox-private

```text
#!/bin/bash
"/mnt/c/Program Files/Mozilla Firefox/firefox.exe" -private-window "$@"
```

And make it executable

```bash
chmod u+x $HOME/bin/firefox-private
```
