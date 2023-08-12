#!/bin/bash
set -e
source .env

cd /opt/star-burger/
echo "Updating project..."
git pull
source env_star_burger/bin/activate
echo "Install requirements..."
pip install -r requirements.txt -q
echo "Install frontend..."
npm ci --dev --quiet --silent
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo "Collect static..."
python manage.py collectstatic --noinput
echo "Migrate..."
python manage.py migrate --noinput
echo "Reload nginx..."
systemctl reload nginx.service

current_commit=$(git rev-parse --verify HEAD)
report_data='{"environment": "production", "revision": '\""$current_commit"\"', "local_username": '\""$USER"\"', "status": "succeeded"}'

curl \
	-H "X-Rollbar-Access-Token: $ROLLBAR_ACCESS_TOKEN" \
	-H "Content-Type: application/json" \
	-X POST "https://api.rollbar.com/api/1/deploy" \
	-d "$report_data"

echo -e "\nDeploy reported to Rollbar"
echo "Deploy completed"

