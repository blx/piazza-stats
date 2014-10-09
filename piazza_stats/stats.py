import csv
import time
import os
import json
import glob
from datetime import datetime
import time
import operator
from itertools import groupby

from pytz import timezone
tz_utc = timezone('UTC')
tz_vancouver = timezone('America/Vancouver')

from pymongo import MongoClient
from piazza_api import PiazzaAPI

from piazza_stats import app


class Stats(object):
    def __init__(self, classid, postsdir):
        self.network_id = classid
        try:
            self.piazza = self.get_piazza()
        except:
            pass
        self.posts = Stats.get_db()
        self.postsdir = postsdir
    
    def get_piazza(self):
        p = PiazzaAPI(network_id=self.network_id)
        p.user_auth(email=app.config["PIAZZA_LOGIN_EMAIL"],
                    password=app.config["PIAZZA_LOGIN_PASS"])
        return p
    
    @staticmethod
    def get_db():
        mongo = MongoClient()
        db = mongo.piazza_db
        return db.posts

    def get_users(self, user_ids):
        return self.piazza.get_users(user_ids)

    def get_posts_by_user(self, user_id):
        username = self.get_users([user_id])[0]

        user_posts = self.posts.find({'result.change_log.0.uid': user_id})
        return [dict(created_by=username, **p.get('result')) for p in user_posts]

    def analyze_time_weights(self):
        def extract_fields(post):
            p = post['result']
            content = p['history'][0]['content']
            return {
                'created': p['created'],
                'tag_good_arr': len(p['tag_good_arr']),
                'unique_views': p['unique_views'],
                'nr': p['nr'],
                'subject': p['history'][0]['subject'],
                'content_preview': content if len(content) < 300 else "%s..." % content[:300],
                'instructor_note': 'instructor-note' in p['tags'],
                'private': p['status'] == 'private'
            }
    
        data = [extract_fields(p)
                for p in self.posts.find()
                if p['result']['status'] != 'deleted']
    
        return data

    def get_calendar(self):
        dates = sorted([p['result']['created'] for p in self.posts.find() if p['result']['status'] != 'deleted'])
    
        days = {}
        for k in [d.split('T')[0] for d in dates]:
            if days.get(k) != None:
                days[k] += 1
            else:
                days[k] = 1
 
        return days
    #    return [{"date":k, "posts":days[k]} for k in sorted(days.keys())]


    def analyze_dir(self, load_db=False):
        if load_db:
            update_db(self.postsdir)
    
        return group_datetimes_by_hours([i["result"]["created"] 
                                         for i in self.posts.find().sort("result.created")
                                         if i["result"].get("created")])
    
    
    def auto_update(self):
        piazza_newest_post = int(self.piazza.get_instructor_stats()['total_posts'])
        db_newest_post = int(self.posts.find().sort("result.change_log.0.when", -1).limit(1)[:][0]['result']['nr'])
        
        if piazza_newest_post <= db_newest_post:
            return
        
        gathered_result = gatherer(self.piazza, db_newest_post + 1, piazza_newest_post, self.postsdir)
        if gathered_result:
            update_db(self.postsdir, db_newest_post + 1, piazza_newest_post)
        else:
            return -len(gathered_result)
        
        return piazza_newest_post - db_newest_post
    
    
    def get_time_until_first_responses(self):
        posts = self.posts.find({"result.status": {"$ne": "deleted"}},
                                {"result.change_log":1, "result.nr":1, "_id":0}).sort("result.nr",1)
        
        posts = [{
            "nr": p["result"]["nr"],
            "created": parse_epoch(p["result"]["change_log"][0]["when"]),
            "first_inst_resp": [parse_epoch(c["when"])
                                for c in p["result"]["change_log"]
                                if c["type"] == "i_answer"][:1],
            "first_stu_resp": [parse_epoch(c["when"])
                               for c in p["result"]["change_log"]
                               if c["type"] == "s_answer"][:1]
        } for p in posts]
       
#            "timedelta_inst": reduce(operator.__sub__,
#                                    [datetime2epoch(parse_datetime(c["when"]))
#                                     for c in p["result"]["change_log"]
#                                     if c["type"] in ["create","i_answer"]][:2][::-1]),
#            "timedelta_stu": reduce(operator.__sub__,
#                                    [datetime2epoch(parse_datetime(c["when"]))
#                                     for c in p["result"]["change_log"]
#                                     if c["type"] in ["create", "s_answer"]][:2][::-1])
#        } for p in posts]
        
        for p in posts:
            p["created_hour"] = datetime.fromtimestamp(p["created"], tz=tz_vancouver).time().hour
            p["timedelta_inst"] = -1 if not p["first_inst_resp"] else p["first_inst_resp"][0] - p["created"]
            p["timedelta_stu"] = -1 if not p["first_stu_resp"] else p["first_stu_resp"][0] - p["created"]
            del p["first_inst_resp"]
            del p["first_stu_resp"]
        
        return posts




def update_db(postsdir, start_post=None, end_post=None):
    posts = Stats.get_db()
    
    for file in glob.iglob(os.path.join(postsdir, '*.json')):
        num = int(os.path.split(file)[1].split('.')[0])

        if start_post and start_post > num:
            continue
        elif end_post and end_post < num:
            break
    
        with open(file, 'r') as infile:
            posts.insert(json.load(infile))
            print 'Added post %s' % file



def gatherer(piazza, start_post, end_post, outdir=None):
    """
    :returns: (if outdir was provided) list of post numbers that had problems and were not saved;
              (else) list of post objects that were successfully retrieved 
    """
    result = []
    delta = end_post - start_post
    
    for i in xrange(start_post, end_post+1):
        print "Fetching post #{}".format(i)
        post = piazza.get_post(cid=i)
        if post and not post.get('error'):
            if outdir:
                with open(os.path.join(outdir, '%d.json' % i), 'w') as outf:
                    json.dump(post, outf)
            else:
                result.append(post)
        elif outdir:
            result.append(i)
        
        if delta > 25 and i % delta == 24:
            time.sleep(3)
        
        time.sleep(1)
    
    return result



def parse_datetime(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=tz_utc).astimezone(tz_vancouver)

def parse_epoch(s):
    return time.mktime(parse_datetime(s).timetuple())


def group_datetimes_by_hours(datetimes):
    hours = {h: 0 for h in xrange(24)}
    for dt in datetimes:
        d = parse_datetime(dt)
        hours[d.hour] += 1
    
    return hours



def time_analyze(json_posts):
    hours = group_datetimes_by_hours(datetimes)
    
    for h in sorted(hours.keys()):
        print 'posts at {}: {}'.format(h, hours[h])

    


def main():
    s = Stats(app.config["PIAZZA_CLASS_ID"])
    p = s.piazza
    
    data = []
    for row in csv.DictReader(p.get_statistics_csv().split("\n")):
        for field in "days online,views,contributions,questions,notes,answers".split(","):
            row[field] = int(row[field])
        data.append(row)
    
    print "CONTRIBUTIONS -- NAME <EMAIL>"
    for row in sorted(data, key=operator.itemgetter('contributions'), reverse=True):
        if row["contributions"] == 0:
            break
        print "{r[contributions]:3d} -- {r[name]} <{r[email]}>{inst}".format(
            r=row,
            inst=" [INSTRUCTOR]" if row["role"] == "Instructor" else "")


if __name__ == "__main__":
    main()