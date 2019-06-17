## Bits

A little [gist](https://gist.github.com/) backed micro blog powered by [App Engine](https://cloud.google.com/appengine/)&mdash;a side project for learning React, Python and App Engine.


### Prerequisite
- Python
  - version 2.7.+ just for running GAE datastore emulator
  - version 3.7.+ for our application
  - use something like [pyenv to manage the versions](https://github.com/pyenv/pyenv)
  - [pip](https://pypi.org/project/pip/) for managing our dependencies
  - [virtualenv](https://virtualenv.pypa.io/en/latest/) for isolating our dependencies (note: includes pip)
- GAE (Google App Engine) SDK
  - make sure to switch to Python 2 at this point, as GAE SDK is not compatible with Python 3
  - [installed and configured](https://cloud.google.com/appengine/docs/standard/python3/quickstart)
  - this will install the `gcloud` cli, which we'll use extensively for development and deployment
- [npm](https://www.npmjs.com/get-npm) for managing our frontend dependencies 
(e.g. React)
- GitHub client key and secret
  - get by [registering a new OAuth application](https://github.com/settings/applications/new)


### Install

#### `gcloud` compoments and datastore emulator
To start we'll make sure we have all the Google `gcloud` components needed for our project. As noted above, `gcloud` only works with Python 2 so we should keep a separate terminal with Python 2 when running `gcloud` commands.

```bash
# If you have penv, 
$ pyenv shell 2.7.4
```

Now install the components we'll need

```bash
# Install the following if not already installed
$ gcloud components install app-engine-python
$ gcloud components install app-engine-python-extras
$ gcloud components install cloud-datastore-emulator
$ gcloud components install gcd-emulator
$ gcloud components install beta
$ gcloud components install gsutil
```
If you ever need to verify any `gcloud` configuration or installed components.
```bash
$ gcloud info
```
Now we can run the [datastore emulator](https://cloud.google.com/datastore/docs/tools/datastore-emulator). Note: `gcloud` stores data at _\<user config dir>/emulators/datastore/WEB-INF/appengine-generated/local_db.bin_. Optionally you can pass `--data-dir=` for a custom location_
```bash
$ gcloud beta emulators datastore start --host-port=localhost:8087
```

#### bits application
In a separate terminal, we'll download, configure and start the bits application.

```bash
# Download the bits code base
$ git clone https://github.com/ikumen/bits.git
$ cd bits
```

If you're using pyenv, it will pick up the `.python-version` (which is set to 3.7.+) file at the root of our project, otherwise set your Python to 3. Now let's isolate our environment and install our dependencies.
```bash
$ virtualenv .venv
$ . .venv/bin/activate
$ (.venv) pip install -r requirements.txt
```

Now we'll configure our backend application, running [Flask](http://flask.pocoo.org/). Our Flask app is configured to pull in properties under `<bits-project>/config/`, specifically a `env`, `local.env`, and `production.env` files. `env` is already provided with some defaults, we'll need to create the `local.env` for development.

```bash
# add <bits-project>/config/local.env, with the following overrides at a minimum
GITHUB_CLIENT_ID=''
GITHUB_CLIENT_SECRET=''
GITHUB_USER_ID='your-github-username'
```

Next we set up our frontend application, by building the JS bundle via [webpack](https://webpack.js.org/). By default the build script will output to a `<bits-project>/public` folder, which
we've map in our Flask app as the [template](http://flask.pocoo.org/docs/1.0/tutorial/templates/) and [static](http://flask.pocoo.org/docs/1.0/tutorial/static/) folders. _Note: the `public` folder gets blown away on every build so don't edit anything in it_.

```bash
# Install dependencies
$ (.venv) npm install
# Builds the Javascript bundle for the frontend app
$ npm run build
```

### Run

Finally run the app with `start-dev.sh` script. Optionally change the emulator host and port in `start-dev.sh` if you're using something different then above steps.

```bash
$ (.venv) . start-dev.sh
```

### Notes

- we are using the newer (as of Nov 2018) Google App Engine standard environment [based on Python 3, not the older Python 2 base environment](https://cloud.google.com/appengine/docs/standard/python3/python-differences)
