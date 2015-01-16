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

    `(piazza_env)$ pip install -r requirements.txt`

7. Start the app in debug mode:
    
    `(piazza_env)$ python runserver.py`


*Post-fetching components powered by [piazza_api](https://github.com/hfaran/piazza-api)*