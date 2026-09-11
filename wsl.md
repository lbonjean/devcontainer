# WSL tips and tricks

## Why WSL

## Filesystem speed

The wsl filesystem is much faster especially if used in bind mounts, in combination with many small files

## Browser variable

In order to avoid device code flow and accounts messing up I use firefox inprivate as browser to authenticate with github, az cli etc. This is how I did this

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
