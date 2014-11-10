import os
from flask import Flask

app = Flask(__name__)
app.config.from_object('piazza_stats.login_config')
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

app.config["POSTS_DIR"] = os.path.join(os.path.dirname(os.path.realpath(__file__)), "posts")


# Do this now that we've created the app object
import piazza_stats.routes
