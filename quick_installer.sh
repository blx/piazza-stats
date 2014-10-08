
# we assume mongo has already been installed and is running

INITIAL_ENV=venv

curl -Lo virtualenv-tmp.tar.gz 'https://github.com/pypa/virtualenv/tarball/master'
mkdir virtualenv-tmp
tar xzf virtualenv-tmp.tar.gz --strip-components 1 -C virtualenv-tmp
python virtualenv-tmp/virtualenv.py $INITIAL_ENV
rm -rf virtualenv-tmp
source $INITIAL_ENV/bin/activate


git clone git@bitbucket.org:bcook/piazza_stats.git

cd piazza_stats
pip install requests pymongo flask

echo 
read -e -p "Piazza username: " PIAZZA_USER
read -s -p "Piazza password: " PIAZZA_PASS
echo 

echo "PIAZZA_LOGIN_EMAIL='$PIAZZA_USER'
PIAZZA_LOGIN_PASS='$PIAZZA_PASS'" > piazza_stats/login_config.py

python runserver.py
