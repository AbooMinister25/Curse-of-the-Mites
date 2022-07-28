## Contributing

Requirements:

- Python 3.10
- Poetry
- NodeJS, some recent version

## Backend

Switch to `server` directory.

```shell
cd server
```

Install dependencies.

```shell
poetry install
```

Install pre-commit. This will run checks on your code every time you try to commit.

```shell
poetry run pre-commit install
```

Run server

```shell
poetry run python3 main.py
```

## Client

Switch to `client` directory.

```shell
cd client
```

Install dependencies.

```shell
poetry install
```

Install pre-commit. This will run checks on your code every time you try to commit.

```shell
poetry run pre-commit install
```

Run the client

```shell
poetry run python3 main.py
```
