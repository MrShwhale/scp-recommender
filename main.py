import pandas as pd
import numpy as np
import code
import sys

OUTPUT_DIR = "./output"
PAGES_PATH = f"{OUTPUT_DIR}/pages.csv"
RATINGS_PATH = f"{OUTPUT_DIR}/ratings.csv"
USERS_PATH = f"{OUTPUT_DIR}/users.csv"
# RATING_MAP_PATH = f"{OUTPUT_DIR}/rating_map.pkl"
RATING_MAP_PATH = f"{OUTPUT_DIR}/short_rating_map.pkl"

def build_pages_frame():
    print("Making pages frame")
    return pd.read_csv(PAGES_PATH)

def build_users_frame():
    print("Making users frame")
    return pd.read_csv(USERS_PATH)

def create_ratings_frame():
    # TODO move this into the spider finishing
    # Instead of a naive read, this should return a dataframe like this:
    #        pageId pageId ...
    # userId rating rating
    # userId rating rating
    # ...
    raw_ratings = pd.read_csv(RATINGS_PATH)

    # Map that takes a pid then uid, and returns a rating
    upmap = {}

    print("Making upmap")

    for (_, uid, pid, rating) in raw_ratings.itertuples():
        if pid not in upmap.keys():
            upmap[pid] = {}

        # Your votes are being detected
        upmap[pid][uid] = int(rating)

    print("Upmap finished")

    # Creates a dataframe with index of pageId and columns of userId
    # It is sparse since density is about 0.2%
    final_frame = pd.DataFrame.from_dict(upmap, dtype=pd.SparseDtype("f2", np.nan))
    print("Pickle-ing")
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

def find_similar(df: pd.DataFrame, uid):
    # For the row at index uid in this df, 
    urow = df.loc[uid]
    uid_mag = np.sqrt((urow ** 2).sum())
    # Create a series of the reciprical of the magnitudes times the uid_mag
    maglist = df.apply(lambda n: (np.sqrt((n ** 2).sum()) * uid_mag) ** -1, axis=1)

    # Then multiply it all together
    similarities = (df @ urow) * maglist
    print(similarities)

    return similarities

if __name__ == "__main__":
    # Your user id is 7904845 btw
    ratings = build_ratings_frame()

    # Who are we looking for
    uid = 6657336

    # Don't normalize ratings, we ball
    # Create similarity matrix
    similar_users = find_similar(ratings, uid)

    # Sort similarity matrix
    similar_users.sort_values(inplace=True, ascending=False) 

    # Drop the value given uid
    similar_users.drop(uid)
    similar_users.head()
