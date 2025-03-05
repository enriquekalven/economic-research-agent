# GHP Chatbot POC

## Repository Structure

This repository is organized as follows:
```
├── server
└── README.md
```

## Environment Setup
Set up a Python virtual environment to localize dependencies:
```sh
# Create venv.
python3 -m venv venv
# Activate venv.
source venv/bin/activate
# Install requirements.
pip install -e .
```

## Running API Server

### Run locally
```sh
uvicorn server.main:app --reload
```


## Linting
The following command lints all python files.

```sh
pylint --jobs=1 $(git ls-files '*.py')
```

