# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
    
## Docker / Compose

Build the Docker image locally:

```bash
docker build -t envirosagro-app:latest .
```

Run with `docker run`:

```bash
docker run -it --rm -p 8501:8501 envirosagro-app:latest
```

Or use `docker-compose` for local development (mounts the repo into the container):

```bash
docker-compose up --build
```

CI: A GitHub Actions workflow is included at `.github/workflows/docker-build.yml` which builds the image on pushes and PRs to `main`.

## Publishing to GitHub Container Registry (GHCR)

The workflow can publish the built image to GHCR when you push to `main`.

What to check/set:
- The workflow uses the automatically provided `GITHUB_TOKEN` to authenticate and requires the workflow permission `packages: write` (already set in the workflow file).
- The image will be published to `ghcr.io/<OWNER>/envirosagro-app:latest`.

If you'd rather publish to Docker Hub, I can update the workflow to use Docker Hub credentials (`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`) stored in repository secrets.

## Development shortcuts (Makefile)

A `Makefile` is included to simplify common tasks:

- `make install` — upgrade `pip` and install pinned requirements from `requirements.txt`.
- `make run` — run the app locally with Streamlit on port `8501`.
- `make docker-build` — build the Docker image locally.
- `make docker-run` — run the built image and expose port `8501`.
- `make compose-up` — run `docker-compose up --build` for development.

Note: `requirements.txt` now pins the current tested versions to help reproducible builds.

    
 ## Demo app

 Run the demo Streamlit app locally:

 ```bash
 pip3 install -r requirements.txt
 streamlit run streamlit_app.py
 ```

 The demo includes a sidebar with dataset controls, a data preview, summary statistics, and a simple time-series chart.
