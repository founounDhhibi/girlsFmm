# Docker

Containerization assets for reproducible deployment.

## Files

- `Dockerfile`: Builds the Python application image.
- `docker-compose.yml`: Runs the app with compose.

## Run

```bash
docker compose -f docker/docker-compose.yml up --build
```

## Notes

For production, run behind a production WSGI server and disable Flask debug mode.
