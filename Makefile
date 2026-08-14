USER=d2435
SERVER=gcp2435

run:
	@cd app && python main.py

push:
	@ssh ${USER}@${SERVER} "mkdir -p /home/${USER}/d2435_invpaz/"
	@scp -r app ${USER}@${SERVER}:/home/${USER}/d2435_invpaz/
	@scp .env ${USER}@${SERVER}:/home/${USER}/d2435_invpaz/.env
	@scp docker-compose.yaml ${USER}@${SERVER}:/home/${USER}/d2435_invpaz/docker-compose.yaml
	@ssh ${USER}@${SERVER} "cd /home/${USER}/d2435_invpaz && docker compose build --no-cache && docker compose up -d --force-recreate && docker system prune -f"

test:
	@cd app && python -m unittest discover -s . -p 'tests.py'