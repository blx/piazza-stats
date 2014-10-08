from piazza_stats import stats

def _update_db(args):
    stats.update_db(args.postsdir, args.start, args.end)

def main_gatherer():
    import sys
    import argparse
    
    aparser = argparse.ArgumentParser()
    aparser.add_argument('action', choices=['fetch', 'update-db'], help='action')
    action = aparser.parse_args(sys.argv[1:2]).action  # slice = "safe get" = no IndexOutOfBounds
    
    if action == 'fetch':
        argparser = argparse.ArgumentParser(description='Download a range of Piazza posts.',
            usage='%(prog)s fetch {start} {end} {postdir}')
        argparser.add_argument('start', type=int, help='post number to start at')
        argparser.add_argument('end', type=int, help='post number to end at')
        argparser.add_argument('postsdir', type=str, help='output directory for posts')
        argparser.add_argument('--update-db', dest='update_db', help='Update mongodb? (default=false)', action='store_true')
        args = argparser.parse_args(sys.argv[2:len(sys.argv)])

        s = stats.Stats(stats.app.config["PIAZZA_CLASS_ID"])
        stats.gatherer(s.piazza, args.start, args.end, args.postsdir)
        
        if args.update_db:
            _update_db(args)
    
    elif action == 'update-db':
        argparser = argparse.ArgumentParser(description='Update the mongodb posts databse.',
            usage='%(prog)s update-db {start} {end} {postdir}')
        argparser.add_argument('start', type=int, help='post number to start at')
        argparser.add_argument('end', type=int, help='post number to end at')
        argparser.add_argument('postsdir', type=str, help='posts directory')
        args = argparser.parse_args(sys.argv[2:len(sys.argv)])
        
        _update_db(args)
    


if __name__ == "__main__":
    main_gatherer()