docker compose down
docker compose up --no-start --build
docker compose run web python manage.py migrate
docker compose run web python manage.py collectstatic --no-input
docker compose run web python manage.py compilemessages -l pt_BR
docker compose up -d --remove-orphans