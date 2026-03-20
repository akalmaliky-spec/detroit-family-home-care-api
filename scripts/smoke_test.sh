#!/usr/bin/env bash
set -e

BASE_URL=$1

echo "Testing health"
curl $BASE_URL/health

echo "Done"