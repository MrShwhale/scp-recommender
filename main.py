import pandas as pd
import numpy as np

OUTPUT_DIR = "./output"
PAGES_PATH = f"{OUTPUT_DIR}/pages.csv"
RATINGS_PATH = f"{OUTPUT_DIR}/ratings.csv"
USERS_PATH = f"{OUTPUT_DIR}/users.csv"
RATING_MAP_PATH = f"{OUTPUT_DIR}/rating_map.pkl"

def build_pages_frame():
    print("Making pages frame")
    return pd.read_csv(PAGES_PATH)

def build_users_frame():
    print("Making users frame")
    return pd.read_csv(USERS_PATH)

def create_ratings_frame():
    # TODO move this into the spider finishing
    # Instead of a naive read, this should return a dataframe like this:
    #        userId userId ...
    # pageId rating rating
    # pageId rating rating
    # ...
    raw_ratings = pd.read_csv(RATINGS_PATH)

    # Map that takes a uid then pid, and returns a rating
    upmap = {}

    print("Making upmap")

    for (_, uid, pid, rating) in raw_ratings.itertuples():
        if uid not in upmap.keys():
            upmap[uid] = {}
        upmap[uid][pid] = rating

    print("Upmap finished")

    # Creates a dataframe with index of pageId and columns of userId
    final_frame = pd.DataFrame.from_dict(upmap)
    final_frame.to_pickle(RATING_MAP_PATH)

    return final_frame

def build_ratings_frame():
    print("Making ratings frame")
    
    WRITE_RMAP = False

    if WRITE_RMAP:
        final_frame = create_ratings_frame()
    else:
        final_frame = pd.read_pickle(RATING_MAP_PATH)

    return final_frame

def build_frames():
    pages = build_pages_frame()
    users = build_users_frame()
    ratings = build_ratings_frame()
    return (ratings, pages, users)

if __name__ == "__main__":
    (ratings, pages, users) = build_frames()
    
