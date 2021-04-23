# Quick Polls

Source code for [quick-polls.xyz](https://quick-polls.xyz/) - service for creating polls and participating in them.

It includes:
- Web server (backend + frontend),
- Full API.

## Installation

Clone this repo and install the dependencies by running:

```bash
$ git clone https://github.com/EnterKeeper/quick-polls.git
$ cd quick-polls
$ pip install -r requirements.txt
```

After that edit `config.py`.

## Running

For development and testing:

```bash
$ python run.py
```

In production:

```bash
$ waitress-serve --call qp:create_app
```

## Authentication

After first running, the `admin` user is created. 
You can log in using:

- Email: `admin@change.email`
- Password: `admin`