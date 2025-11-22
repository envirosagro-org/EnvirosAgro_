install:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r requirements.txt

run:
	streamlit run streamlit_app.py --server.port 8501 --server.headless true

docker-build:
	docker build -t envirosagro-app:latest .

docker-run:
	docker run -it --rm -p 8501:8501 envirosagro-app:latest

compose-up:
	docker-compose up --build

.PHONY: lint

lint:
	python3 -m pip install --upgrade pip
	python3 -m pip install -r dev-requirements.txt
	ruff check . --fix
	pre-commit run --all-files --show-diff-on-failure

.PHONY: install run docker-build docker-run compose-up
