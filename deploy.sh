#!/bin/bash
set -e

cd /opt/star-burger/
git pull
source env_star_burger/bin/activate
pip install -r requirements.txt -q
npm ci --dev --silent
./node_modules/.bin/parcel watch bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate --noinput

systemctl reload nginx.service


echo "Deploy completed"

