#!/bin/bash

# Check that we have got 1 parameter if not print usage
[ $# -ne 1 ] && { echo "Usage: $0 <number of certificates>"; exit 1; }

# Change directory
cd cert

# Run the gen-cert N times
for ((n=0;n<${1};n++))
do
    # Every iteration change the name and IP address (starts from 172.26.7.2 to avoid using the NS's IP)
    ./gen-cert.sh node${n} 172.26.$((n+2>=6 ? n+3 : n+2)).1
    ./gen-cert.sh store${n} 172.26.$((n+2>=6 ? n+3 : n+2)).2
done