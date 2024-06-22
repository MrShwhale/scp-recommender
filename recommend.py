import numpy as np
import pandas as pd
import scipy.stats
from sklearn.metrics.pairwise import cosine_similarity

# The minimum number of rating to consider someone's opinion
MIN_RATINGS_THRESHOLD = 5

# The maximum number of similar users to base the recommendations on
MAX_SIMILAR_USERS = 10

# Turn the ratings from a raw dict to a matrix
def process_data(raw_ratings: pd.DataFrame) -> pd.DataFrame:
    # Make this sparse
    rating_map = raw_ratings.pivot_table(index="userId", columns="pageId", values="rating", fill_value=0)
    rating_map.astype(pd.SparseDtype(np.float32, 0), copy=False)

    # Filter out people with very few entries
    # Absolute value thing ONLY WORKS since the downvotes and upvotes are both 1
    rating_map = rating_map.loc[rating_map.abs().sum(axis=1) >= MIN_RATINGS_THRESHOLD]
    return rating_map

# Modifies the given rating map in-place
def normalize_data(rating_map: pd.DataFrame) -> None:
    # SCP users have this nasty habit of being positive people.
    # This means that they mostly only upvote, which causes issues since then the average for many rows is 0
    # This could be a critical issue but if you knew what you were doing you wouldn't be here at all
    # So, change the average rating to be the mean but with a single 0 rating added

    # TODO check if it is faster to add/remove a fake page with rating 0 for all users and use mean
    norm_factor = rating_map.sum(axis=1) / (rating_map.count(axis=1) + 1)
    rating_map = rating_map.subtract(norm_factor, axis="rows")

def generate_similarity(rating_map: pd.DataFrame) -> pd.DataFrame:
    # TODO this probably has a better way to do it
    # That sentence probably has a better way to do it too
    similar_users = cosine_similarity(rating_map)
    similar_users = pd.DataFrame(similar_users, index=rating_map.index, columns=rating_map.index)
    # Only the index has the uid, not the columns as in PPMC
    return similar_users

def find_similar_users(similarity_matrix: pd.DataFrame, uid: int) -> pd.DataFrame:
    similar = similarity_matrix.loc[uid]
    similar.drop(uid, inplace=True)
    similar.sort_values(inplace=True, ascending=False)
    return similar

def get_recomendations(similarity_matrix: pd.DataFrame, rating_map: pd.DataFrame, uid: int):
    # Consider saving an old copy of rating_map to the disk rather than keeping both in memory
    read_pages = rating_map[uid]

    # Drop all the pages the user hasn't read
    # https://stackoverflow.com/questions/22649693/drop-rows-with-all-zeros-in-pandas-data-frame
    read_pages = read_pages.loc[(read_pages!=0).all(axis=1)]
    
    # Get pages read by the most similar users
    # TODO refactor or at least understand this line, you copied it in an airport
    similar_pages = rating_map[rating_map.index.isin(similarity_matrix.head(10).index)]
    similar_pages = similar_pages.loc[(similar_pages!=0).all(axis=1)]

    # Remove all pages the user has read from the recommendations
    similar_pages = similar_pages.drop(read_pages.columns, axis=1, inplace=True, errors="ignore")

    print(similar_pages)

    return similar_pages

if __name__ == "__main__":
    # Step 0: Set limits (delete for production)
    import resource
    soft, hard = resource.getrlimit(resource.RLIMIT_AS) 
    resource.setrlimit(resource.RLIMIT_AS, (20_000_000_000, 25_000_000_000)) 

    # Step 1: Read raw data
    print("Reading raw data...")
    raw_ratings = pd.read_csv("./output/ratings.csv", dtype={"userId":np.int64, "pageId":np.int64, "rating":np.float32})

    # Step 2: Process data
    print("Processing raw data...")
    rating_map = process_data(raw_ratings)

    # Clean up old dataframe
    del raw_ratings

    # Step 3: Normalize data
    print("Normalizing data...")
    normalize_data(rating_map)

    # Step 4: Find similar users
    print("Generating user similarity matrix...")
    similar_users = generate_similarity(rating_map)

    # At this point the model is done. The rest is recommendations!

    # Get input from the user about what they want and for which user
    user_map = pd.read_csv("./output/users.csv")
    page_map = pd.read_csv("./output/pages.csv")
    while (True):
        # UID for test: 28829
        print("Mode selection: ")
        print("1. Get users similar to another user.")
        print("2. Get recommendations for a user.")
        print("3. Get username from uid.")
        print("4. Get uid from username")
        user_in = input()
        if user_in == "1":
            print("Enter your user id: ", end="")
            user_in = input()
            try:
                uid = int(user_in)
                similar = find_similar_users(similar_users, uid)
                print(similar)
            except:
                print("Couldn't find that uid")
        elif user_in == "2":
            try:
                uid = int(user_in)
                similar = find_similar_users(similar_users, uid)
                recommendations = get_recomendations(similar, rating_map, uid)
            except:
                print("Couldn't find that uid")
        elif user_in == "3":
            print("Enter your user id: ", end="")
            user_in = input()
            try:
                uid = int(user_in)
                print(user_map.loc[user_map["userId"] == uid]["userName"].iloc[0])
            except:
                print("Couldn't find that uid")
        elif user_in == "4":
            print("Enter your user name: ", end="")
            user_in = input()
            try:
                print(user_map.loc[user_map["userName"] == user_in]["userId"].iloc[0])
            except:
                print("Couldn't find that name")
        else:
            print("I do not know what that means.")
