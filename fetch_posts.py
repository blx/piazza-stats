def main_gatherer():
    import argparse
    from piazza_stats import stats
    
    argparser = argparse.ArgumentParser(description='Download a range of Piazza posts.')
    argparser.add_argument('start', type=int, help='post number to start at')
    argparser.add_argument('end', type=int, help='post number to end at')
    argparser.add_argument('outdir', type=str, help='output directory for posts')
    args = argparser.parse_args()
    
    s = stats.Stats(stats.app.config["PIAZZA_CLASS_ID"])
    p = s.piazza
    
    stats.gatherer(p, args.start, args.end, args.outdir)

if __name__ == "__main__":
    main_gatherer()