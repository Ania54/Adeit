#!/bin/bash

# Redirect stdout and stderr to tee
exec > >(tee -a update.txt) 2>&1

# Your script commands
cd ~/Adeit
git checkout -- deploy.sh
git pull origin master

# Append two newlines after all output
echo -e "\n\n" >> update.txt