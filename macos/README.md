# macos install docs

To create a venv for macos (for cursor)

```
/usr/local/bin/python3.9 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip

pip install -r requirements-mac-arm64.txt

pip install -r requirements.txt

pip install -r requirements.txt --no-deps

pip install spektral
```
