from flask import Flask

app = Flask(__name__)
app.config.from_object('piazza_stats.login_config')
app.config["PIAZZA_CLASS_ID"] = "hx2lqx3ohi06j"
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0


# Do this now that we've created the app object
import piazza_stats.routes
