#!/bin/bash
set -e
cd /opt/star-burger
git pull origin master
. venv/bin/activate
pip install -r requirements.txt
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python3 manage.py collectstatic --noinput
python3 manage.py migrate --noinput
systemctl restart starburger
systemctl reload nginx
set -o allexport
source .env
set +o allexport
curl -H "X-Rollbar-Access-Token: ${ROLLBAR_API_KEY}" -H "Content-Type: application/json" -X POST 'https://api.rollbar.com/api/1/deploy'>echo -e "\n--- Successful deploy ---\n"
echo -e "\n--- Successful deploy ---\n"
