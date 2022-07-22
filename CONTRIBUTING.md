## Contributing

Quick notes before I forget them, please rewrite this!

Requirements:
 - Python 3.10
 - Poetry
 - NodeJS, some recent version

Installation of Python dependencies: `poetry install`.

For the webapp (`/web`):
 - Install dependencies via `npm install`.
 - Build project via `npm run build` or `npm run dev` for auto-build.

For development use: (no need to run multiple times)

`poetry run uvicorn main:app --reload`

For deployment that should be:

`poetry run uvicorn main:app --host 0.0.0.0 --port 80`
