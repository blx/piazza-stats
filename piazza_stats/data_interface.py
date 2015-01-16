import os
import json
import glob
from time import sleep

from piazza_api.rpc import PiazzaRPC as PiazzaAPI
from pymongo import MongoClient
from bson import json_util

from piazza_stats import app


def get_piazza(network_id=None, email=None, password=None):
    p = PiazzaAPI(network_id=network_id or app.config["PIAZZA_CLASS_ID"])
    p.user_login(email=email or app.config["PIAZZA_LOGIN_EMAIL"],
                 password=password or app.config["PIAZZA_LOGIN_PASS"])
    return p


def get_db():
    return MongoClient().piazza_db.posts



def update_db(postsdir, start_post=None, end_post=None):
    posts = get_db()
    
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
    Fetches Piazza posts with numbers in the range [start_post, end_post] and
    either returns them as a list of objects or writes them as JSON to the provided
    outdir. If outdir is given, the posts are also pushed to the database.
    
    :returns: (if outdir was provided) list of post numbers that had problems and were not saved;
              (else) list of post objects that were successfully retrieved 
    """
    result = []
    delta = end_post - start_post
    db = get_db()
    
    for i in xrange(start_post, end_post+1):
        print "Fetching post #{}".format(i)
        post = piazza.get(cid=i)
        if post and not post.get('error'):
            if outdir:
                db.insert(post)
                print 'Added post %d to db' % i
                
                with open(os.path.join(outdir, '%d.json' % i), 'w') as outf:
                    outf.write(json_util.dumps(post, outf))
            else:
                result.append(post)
        elif outdir:
            result.append(i)
        
        if delta > 25 and not i % 25:
            sleep(3)
        
        sleep(1)
    
    return result




def main_gatherer():
    import sys
    import argparse
    
    aparser = argparse.ArgumentParser()
    aparser.add_argument('action', choices=['fetch', 'update-db'], help='action')
    action = aparser.parse_args(sys.argv[1:2]).action  # slice = "safe get" = no IndexOutOfBounds
    
    if action == 'fetch':
        argparser = argparse.ArgumentParser(description='Download a range of Piazza posts and push them to the database.',
            usage='%(prog)s fetch {start} {end} {postdir}')
        argparser.add_argument('start', type=int, help='post number to start at')
        argparser.add_argument('end', type=int, help='post number to end at')
        argparser.add_argument('postsdir', type=str, help='output directory for posts')
        args = argparser.parse_args(sys.argv[2:len(sys.argv)])

        p = get_piazza()
        gatherer(p, args.start, args.end, args.postsdir)
        
    
    elif action == 'update-db':
        argparser = argparse.ArgumentParser(description='Update the mongodb posts databse.',
            usage='%(prog)s update-db {start} {end} {postdir}')
        argparser.add_argument('start', type=int, help='post number to start at')
        argparser.add_argument('end', type=int, help='post number to end at')
        argparser.add_argument('postsdir', type=str, help='posts directory')
        args = argparser.parse_args(sys.argv[2:len(sys.argv)])
        
        update_db(args.postsdir, args.start, args.end)
    


if __name__ == "__main__":
    main_gatherer()