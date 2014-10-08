from flask import render_template, jsonify, request, abort

from piazza_stats import app
from piazza_stats.stats import Stats

# Cache the stats object between requests to preserve
# the PiazzaAPI and Mongo connections.
stats = Stats("hx2lqx3ohi06j")



@app.route('/')
def dashboard_view():
    return render_template('dashboard.html')

@app.route('/get_users', methods=['POST'])
def get_users_json():
    if not request.json or not 'users' in request.json:
        abort(400)
    return jsonify({"data":stats.get_users(request.json['users'])})

@app.route('/user/<uid>/posts')
def get_user_posts(uid):
    return jsonify({"data":stats.get_posts_by_user(uid)})

@app.route('/times/json')
def get_times_json():
    return jsonify({"data":[{"hour":k, "frequency":v} for k, v in stats.analyze_dir('posts').items()]})
    
@app.route('/posts-weights/json')
def get_posts_weights_json():
    return jsonify({"data":stats.analyze_time_weights()})

@app.route('/calendar/json')
def get_calendar_json():
    return jsonify({"data":stats.get_calendar()})

@app.route('/instructor_stats')
def get_instructor_stats():
    return jsonify({"data":stats.piazza.get_instructor_stats()})
