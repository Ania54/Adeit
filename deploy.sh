#!/bin/bash

# Redirect all output to a log file (append mode)
exec >> update.txt 2>&1

# Your script commands
cd ~/Adeit
git pull origin master

# Append two newlines after all output
echo -e "\n\n" >> update.txt