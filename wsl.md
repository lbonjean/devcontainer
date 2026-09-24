# WSL tips and tricks

## Why WSL

## Filesystem speed

The wsl filesystem is much faster especially if used in bind mounts, in combination with many small files

## Browser variable

In order to avoid device code flow and accounts messing up I use firefox inprivate as browser to authenticate with github, az cli etc. This is how I did this

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
