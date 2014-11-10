# piazza_stats

by Ben Cook <b@bencook.ca>

### Installation:
 
1. Download piazza_stats:

    `$ git clone piazza_stats`

2. Create new virtualenv:

    `$ virtualenv piazza_env`

3. Setup Piazza login configuration:

    ```
    $ echo "PIAZZA_LOGIN_EMAIL=(email)
    > PIAZZA_LOGIN_PASS=(pass)" > piazza_stats/login_config.py
    ```

4. Activate virtualenv:
    
    `$ source piazza_env/bin/activate`

5. In a separate Terminal, find and activate MongoDB:
    
    `$ mongod --dbpath (dbpath)`

6. Back in the virtualenv, install packages:

    `(piazza_env)$ pip install pymongo flask pytz pyjade`

    ```
    (piazza_env)$ pip install requests
    (piazza_env)$ cd piazza_env/lib/python2.7/site-packages
    (piazza_env)$ git clone git@github.com:hfaran/piazza-api.git piazza_api
    (piazza_env)$ ln -s piazza_api/piazza_api.py piazza_api/__init__.py
    ```
    
    (until we get the packaging correct, at which point this will be pip install piazza_api)
    
    (check out [piazza_api by hfaran on github](https://github.com/hfaran/piazza-api) for more info)

7. Start the app in debug mode:
    
    `(piazza_env)$ python runserver.py`
