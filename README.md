## Task Management Tool
### How to
1. Download repository
2. Install docker and docker compose (v1.28+) e.g.

        apt install docker docker-compose

3. From main project directory run application using docker compose

        docker compose up --build

4. To access swagger documentation go to http://127.0.0.1:8000/docs#

5. For testing use this command

        docker compose build tests && docker compose --profile tests run --rm tests