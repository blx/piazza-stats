# piazza_stats

by Ben Cook <b@bencook.ca>

### Installation:
 
1. Download piazza_stats:

    `$ git clone piazza_stats`

2. Create new virtualenv:

    `$ virtualenv piazza_env`

3. Setup Piazza login configuration:

    `$ echo "PIAZZA_LOGIN_USER=(user)`
    `> PIAZZA_LOGIN_PASS=(pass) > piazza_stats/login_config.py"`

4. Activate virtualenv:
    
    `$ source piazza_env/bin/activate`

5. In a separate Terminal, find and activate MongoDB:
    
    `$ mongod --dbpath (dbpath)`

6. Back in the virtualenv, install packages:

    `(piazza_env)$ pip install requests pymongo flask`

7. Start the app:
    
    `(piazza_env)$ python runserver.py`


### Credits:

Includes code based on [piazza_api by hfaran on github](https://github.com/hfaran/piazza-api), licensed as follows:

>The MIT License (MIT)

>Copyright (c) 2013 Hamza Faran

>Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

>The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

>THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
