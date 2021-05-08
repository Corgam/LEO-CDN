#!/bin/bash

# Check that we have got 1 parameter if not print usage
[ $# -ne 1 ] && { echo "Usage: $0 <number of certificates>"; exit 1; }

# Change directory
cd cert

# Run the gen-cert N times
maxN=${1}
n=0
while (( n  < maxN ))
do
    # Every iteration change the name and IP address (starts from 172.26.7.2 to avoid using the NS's IP)
    ./gen-cert.sh node${n} 172.26.$((n+7)).1
    ./gen-cert.sh store${n} 172.26.$((n+7)).2
    n=$((n+1))
done