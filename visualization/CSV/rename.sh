#!/usr/bin/env bash
for f in *.csv; do mv "$f" "$(echo "$f" | sed s/.*Broker/input-Broker/)"; done
