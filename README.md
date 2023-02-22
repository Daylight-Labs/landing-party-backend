Back-end for Landing Party Bot

Bot is located here: https://github.com/Daylight-Labs/landing-party-bot

# Tech Stack:
- Python Django
- Postgres database
- django-background-tasks for background tasks

# Running/deploying
- Install dependencies
- Fill environmental variables (list is specified in docker-compose.yml)
- Both backend and bot need to point to same Postgres database
- CHATBOT_API_AUTH_TOKEN env variable needs to be the same for bot and back-end
- Backend URL needs to stored in bot as env variable
- If there will be a lot of users using bot simultaneously, it's recommended to have auto-scalable cluster of back-end instances instead of just one server. Also it's recommended to have a separate instance for django-background-tasks worker.
- Run db migrations (python manage.py migrate) before running server


Provided "as is", without warranty of any kind