import csv
import time
from datetime import datetime
import operator

from pytz import timezone
TZ_UTC = timezone('UTC')
TZ_VANCOUVER = timezone('America/Vancouver')

from piazza_stats import app
from piazza_stats import data_interface


class Stats(object):
    def __init__(self, nid=None, postsdir=None):
        self.network_id = nid or app.config["PIAZZA_CLASS_ID"]
        self.piazza = data_interface.get_piazza(network_id=self.network_id)
        self.posts = data_interface.get_db()
        self.postsdir = postsdir or app.config["POSTS_DIR"]


    def get_users(self, user_ids):
        return self.piazza.get_users(user_ids)

    def get_posts_by_user(self, user_id):
        username = self.get_users([user_id])[0]

        user_posts = self.posts.find({'change_log.0.uid': user_id})
        return [dict(created_by=username, **p)
                for p in user_posts]

    def analyze_time_weights(self):
        def extract_fields(p):
            content = p['history'][0]['content']
            return {
                'created': p['created'],
                'tag_good_arr': len(p['tag_good_arr']),
                'unique_views': p['unique_views'],
                'nr': p['nr'],
                'subject': p['history'][0]['subject'],
                'content_preview': content if len(content) < 300
                                   else "%s..." % content[:300],
                'instructor_note': 'instructor-note' in p['tags'],
                'private': p['status'] == 'private'
            }

        data = [extract_fields(p)
                for p in self.posts.find()
                if p['status'] != 'deleted']

        return data

    def get_calendar(self):
        dates = [p['created'].split('T')[0]
                 for p in self.posts.find(
                    {"status": {"$ne": "deleted"}},
                    {"created": 1}
                 ).sort("created")]

        days = {}
        for k in dates:
            if days.get(k) != None:
                days[k] += 1
            else:
                days[k] = 1

        return days


    def analyze_dir(self):
        return group_datetimes_by_hours([p["created"]
                                         for p in self.posts.find(
                                            {"created": {"$exists": True}}
                                         ).sort("created")])


    def auto_update(self):
        piazza_newest_post = int(self.piazza.get_stats()['total']['posts'])
        db_newest_post = int((self.posts.find()
                                        .sort("change_log.0.when", -1)
                                        .limit(1)[:][0]['nr']))

        if piazza_newest_post <= db_newest_post:
            return

        gathered_result = data_interface.gatherer(self.piazza,
                                                  db_newest_post + 1,
                                                  piazza_newest_post,
                                                  self.postsdir)

        return piazza_newest_post - db_newest_post


    def get_time_until_first_responses(self):
        posts = self.posts.find({"status": {"$ne": "deleted"}},
                                {"change_log": 1, "nr" :1, "_id": 0}
                               ).sort("nr")

        posts = [{
            "nr": p["nr"],
            "created": parse_epoch(p["change_log"][0]["when"]),
            "first_inst_resp": [parse_epoch(c["when"])
                                for c in p["change_log"]
                                if c["type"] == "i_answer"][:1],
            "first_stu_resp": [parse_epoch(c["when"])
                               for c in p["change_log"]
                               if c["type"] == "s_answer"][:1]
        } for p in posts]

        for p in posts:
            p["created_hour"] = time.localtime(p["created"]).tm_hour
            p["timedelta_inst"] = -1 if not p["first_inst_resp"] \
                                     else p["first_inst_resp"][0] - p["created"]
            p["timedelta_stu"] = -1 if not p["first_stu_resp"] \
                                    else p["first_stu_resp"][0] - p["created"]
            del p["first_inst_resp"]
            del p["first_stu_resp"]

        return posts

    def get_users(self):
        pass



def parse_datetime(s):
    return (datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
            .replace(tzinfo=TZ_UTC)
            .astimezone(TZ_VANCOUVER))

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




def process_csv(csvstr=""):
    if not csvstr:
        csvstr = Stats().piazza.get_statistics_csv()

    data = []
    for row in csv.DictReader(csvstr.split("\n")):
        for field in "days online,views,contributions,questions,notes,answers".split(","):
            row[field] = int(row[field])
        data.append(row)

    print "CONTRIBUTIONS -- NAME <EMAIL>"
    for row in sorted(data, key=operator.itemgetter('contributions'), reverse=True):
        if row["contributions"] == 0:
            break
        print "{r[contributions]:4d} -- {r[name]} <{r[email]}>{inst}".format(
            r=row,
            inst=" [INSTRUCTOR]" if row["role"] == "Instructor" else "")


if __name__ == "__main__":
    process_csv()
