First, install the requirements using `pip`, for example using `virtualenv`:

    virtualenv env
    source env/bin/activate
    pip install -r requirements.txt

(If you find that there are still some requirements missing, please add them to requirements.txt.)

Next, you need to create a fresh configuration file and fetch the OAuth2 API keys:

    cp fitbit.cfg.example fitbit.cfg
    ./gather_keys_oauth2.py

Open the file `upload.py` in your favourite text editor and check the variables at the start of the file, at least the DiMe username and password.  Finally, run it to import your Fitbit events into DiMe:

    ./upload.py

Currently the script takes the steps at 15 minute intervals, but this can be changed by altering the variables.  It also takes the values just for today.  See the Python fitbit library's API for how to other things: <http://python-fitbit.readthedocs.io/en/latest/>
