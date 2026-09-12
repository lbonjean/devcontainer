# Environment configuration

A properly configured environment is important and makes your live easier. Especially if using several identities.
To separate all these identities I user firefox in private, but you can use whatever browser you want.

Variables:

- BROWSER: used by az,gh,
- GH_BROWSER: Overrides BROWSER if specigied for GH

## Cmd

Do ths once for your user account
setx GH_BROWSER "C:/users/c0000-luc/.config/lucsettings/firefox.cmd"
setx BROWSER "\"C:/Program Files/Mozilla Firefox/firefox.exe\" -private-window %%s"

Contents of the file:  

```text
@echo off
start "" "C:\Program Files\Mozilla Firefox\firefox.exe" -private-window "%*"
```

## Powershell

Powershell inherits what is defined with setx, but the syntax is not allways compatible
Add this to your profile (code $PROFILE)

```text
$env:BROWSER = '"C:\\Program Files\Mozilla Firefox\\firefox.exe" -private-window %s'
```

## WSL / Linux

### In .bashrc

export BROWSER="$HOME/bin/firefox-private"

### In $HOME/bin/firefox-private

```text
#!/bin/bash
"/mnt/c/Program Files/Mozilla Firefox/firefox.exe" -private-window "$@"
```

And make it executable

```bash
chmod u+x $HOME/bin/firefox-private
```
