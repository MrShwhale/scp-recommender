import pandas as pd
import numpy as np

OUTPUT_DIR = "./output"
PAGES_PATH = f"{OUTPUT_DIR}/pages.csv"
RATINGS_PATH = f"{OUTPUT_DIR}/ratings.csv"
USERS_PATH = f"{OUTPUT_DIR}/users.csv"

def build_pages_frame():
    print("Making pages frame")
    return pd.read_csv(PAGES_PATH)

def build_users_frame():
    print("Making users frame")
    return pd.read_csv(USERS_PATH)

def build_ratings_frame():
    print("Making ratings frame")

def build_frames():
    pages = build_pages_frame()
    users = build_users_frame()
    ratings = build_ratings_frame()
    return (ratings, pages, users)

if __name__ == "__main__":
    (ratings, pages, users) = build_frames()
