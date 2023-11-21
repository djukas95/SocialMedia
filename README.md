# Social Media - Flask app

## Create **venv**
### Windows
    python -m venv venv
### Linux/MacOS
    python3 -m venv venv

## Activate **venv** 
### Windows
    venv\Scripts\activate
### Linux/MacOS
    source venv/bin/activate

## Install requirements
    pip install "cython<3.0.0" wheel
    pip install "pyyaml==5.4.1" --no-build-isolation
    pip install -r requirements.txt

## Set FLASK_APP
    set FLASK_APP=app.py

## Run app 
    flask run

