sudo apt update

sudo apt install -y build-essential curl git libssl-dev zlib1g-dev   libbz2-dev libreadline-dev libsqlite3-dev libffi-dev liblzma-dev

curl https://pyenv.run | bash

export PATH="$HOME/.pyenv/bin:$PATH"

eval "$(pyenv init -)"

eval "$(pyenv virtualenv-init -)"  

pyenv install 3.10.14


pyenv virtualenv 3.10.14 chatbot-py 

pyenv activate chatbot-py

pip install --upgrade pip setuptools

pip install pip-tools

pip-sync requirements.txt

python3 --version

python3 start.py




## Herramientas de desarrollo (opcional)

pip install -r requirements.txt -r requirements-dev.txt

ruff format src tests

ruff check src tests

pre-commit install




