# Betting software test assignment

# Setting up the environment
Write an .env file with the following fields filled in project root directory
```
POSTGRESQL_DB=
POSTGRESQL_USER=
POSTGRESQL_PASSWORD=
POSTGRESQL_HOST=
POSTGRESQL_PORT=
```

Also dont forget to run migrations
```bash
docker exec -it backend_web_1 bash
alembic upgrade head
```

# Manual deployment
Assuming you have poetry package manager installed
```bash
poetry install
```

# Manual running
```bash
source ./venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8090
```

# Running tests
Assuming you have Docker installed locally because tests 
are dependent on testcontainers package to run postgresql container
```bash
source ./venv/bin/activate
pytest
```

# Local deployment using docker-compose
Please remember the line provider service code comes from
https://github.com/SuminAndrew/bsw-test-line-provider which is a service for testing, if you want to change this service write your own line provider and change link of a build instruction in docker-compose.yml file
```bash
docker-compose up --build
```

