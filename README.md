# PercGuru

## Requirements
- Python >=3.8
- Postgres

## Dev setup
1.  Run an instance of postgres using docker or podman
```shell
podman run -p 5432:5432 --name some-postgres -e POSTGRES_PASSWORD=mysecretpassword -d postgres
```

2. (Recommended) Create a virtual environment
```shell
python3 -m venv venv
source venv/bin/activate
```

3. Install the python requirements
```shell
pip install -r requirements.txt
```

4. Run `main.py` with the following environment variables set
```text
DB_USERNAME
DB_PASSWORD
DB_HOST
BOT_TOKEN
```
