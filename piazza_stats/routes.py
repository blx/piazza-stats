from flask import render_template, jsonify, request, abort

from piazza_stats import app
from piazza_stats.stats import Stats

courseID = app.config["PIAZZA_CLASS"] = app.config["PIAZZA_CLASSES"].keys()[0]
course = app.config["PIAZZA_CLASSES"][courseID]

# Cache the stats object between requests to preserve
# the PiazzaAPI and Mongo connections.
stats = Stats(nid=courseID)


def js(obj):
    return jsonify({"data":obj})


@app.route('/')
def dashboard_view():
    return render_template('dashboard.jade', course=course)

@app.route('/get_users', methods=['POST'])
def get_users_json():
    if not request.json or not 'users' in request.json:
        abort(400)
    return js(stats.get_users(request.json['users']))

@app.route('/user/<uid>/piazza_stats')
def get_user_posts(uid):
    return js(stats.get_posts_by_user(uid))

@app.route('/times/json')
def get_times_json():
    return js([{"hour":k, "frequency":v}
               for k, v in stats.analyze_dir().items()])

@app.route('/posts-weights/json')
def get_posts_weights_json():
    return js(stats.analyze_time_weights())

@app.route('/calendar/json')
def get_calendar_json():
    return js(stats.get_calendar())

@app.route('/auto-update')
def run_auto_update():
    return js({"update_count": stats.auto_update()})

@app.route('/time-until-responses')
def get_time_until_first_resp():
    return js(stats.get_time_until_first_responses())

@app.route('/posts')
def get_all_posts():
    return js(list(stats.posts.find({},
                                    {"nr":1, "_id":0}
                                   ).sort("nr", -1)))
