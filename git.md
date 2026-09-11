# git en github ticks and tips

## multiple accounts

Make sue you have a recent version of gh check with gh --version

- on the host log in with gh auth login with all your accounts (personal and enterprise)
- these settings are inherited bij the devcontainer, but you will not see it with git auth status.  
You can check in the devcontainer that ther is a helper:  

``` text
git config --global --get-all credential.helper
```

- if you have to clone from with different accounts put your github account after https://  
eg git clone <https://lbonjean@github.com/lbonjean/devcontainer.git>  
The correct account wil be selected.
