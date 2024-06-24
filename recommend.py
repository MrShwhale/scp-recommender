import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# The minimum number of votes to consider someone's opinion
MIN_RATINGS_THRESHOLD = 5

# The maximum number of similar users to base the recommendations on
MAX_SIMILAR_USERS = 10

# The maximum number of recommendations to show to the user
MAX_RECOMMENDATIONS_LISTED = 10

# Turn the ratings from a raw dict to a user-page matrix (rating map)
def process_data(raw_ratings: pd.DataFrame) -> pd.DataFrame:
    rating_map = raw_ratings.pivot_table(index="userId", columns="pageId", values="rating", fill_value=0)

    # Make the above sparse (will not help if the original is too big to hold it)
    # BUG For some reason, actually making this a sparse matrix will crash things on line 24 when it runs out of memory
    # My best guess is that .abs() creates a full version of the matrix for some reason
    # rating_map = rating_map.astype(pd.SparseDtype(np.float32, 0), copy=True)

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

    norm_factor = rating_map.sum(axis=1) / (rating_map.count(axis=1) + 1)
    rating_map = rating_map.subtract(norm_factor, axis="rows")

# Makes a map which shows how similar each user is to each other user
def generate_similarity(rating_map: pd.DataFrame) -> pd.DataFrame:
    # TODO There is probably a better way to do this
    # Specifically, one where only the similarity to the user is generated rather than everyone's similarities
    similar_users = pd.DataFrame(cosine_similarity(rating_map), index=rating_map.index, columns=rating_map.index)

    # Drop all times where the user is compared to itself
    similar_users = similar_users.loc[similar_users.index != similar_users.columns]
    return similar_users

# Returns a sorted DataFrame with all of the most similar_users to a given user
def find_similar_users(similarity_matrix: pd.DataFrame, uid: int) -> pd.DataFrame:
    # TODO why is this a dataframe and not series?
    similar = similarity_matrix.loc[uid].sort_values(inplace=False, ascending=False)
    return similar

# Return the recommendations for the given user based on similar users and what those users liked
def get_recomendations(similarity_matrix: pd.DataFrame, rating_map: pd.DataFrame, uid: int) -> pd.Series:
    # Consider saving an old copy of rating_map to the disk rather than keeping both in memory
    read_pages = rating_map[rating_map.index == uid]

    # Drop all the pages the user hasn't read
    read_pages = read_pages.loc[uid, read_pages.iloc[0] != 0]

    # Get pages read by the most similar users
    # TODO refactor or at least understand this line, you copied it in an airport
    most_similar_users = similarity_matrix.head(10)
    similar_pages = rating_map[rating_map.index.isin(most_similar_users.index)]

    # This might be VERY slow, idk
    similar_pages = similar_pages.loc[:, similar_pages.any(axis=0)]

    # Remove all pages the user has read from the recommendations
    similar_pages.drop(read_pages.index, axis=1, inplace=True, errors="ignore")

    # Simple dot weight algorithm
    # Could run into the issue that with multiple people
    def dot_weight(votes):
        return most_similar_users.values @ votes

    # More complex weighting that takes slightly reduces "popularity bias"
    # def whale_weight(votes):
    #     return most_similar_users.values @ votes

    similar_pages = similar_pages.apply(dot_weight, axis=0)
    similar_pages.sort_values(ascending=False, inplace=True)

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

    while True:
        # Ask for the username
        while True:
            print("Username: ", end="")
            username = input()
            try:
                uid = user_map.loc[user_map["userName"] == username]["userId"].iloc[0]
                break
            except:
                print("We can't find that username. Make sure you have the caps right and everything.")

        print(f"Getting recommendations for {username}...")
        try:
            similar = find_similar_users(similar_users, uid)
        except:
            print(f"You must have at least {MIN_RATINGS_THRESHOLD} pages voted on to use this tool! Come back with more votes when this updates.")
            continue

        recommendations = get_recomendations(similar, rating_map, uid)
        print("Recommendations:")

        i = 0
        for rec in recommendations.index:
            if i >= MAX_RECOMMENDATIONS_LISTED:
                break
            print(f"{page_map.loc[page_map['pageId'] == rec]['title'].iloc[0]}")
            i += 1
