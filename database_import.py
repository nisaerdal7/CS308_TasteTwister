import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy import inspect

# Function to read CSV file
def read_csv(file_path):
    try:
        return pd.read_csv(file_path, on_bad_lines='skip')
    except FileNotFoundError:
        return pd.DataFrame()  # Return empty dataframe if file is not found
    except pd.errors.ParserError as e:
        print(f"Error reading {file_path}: {e}")
        return pd.DataFrame()


# Function to get user input for column mapping
def get_column_mapping(df_columns, table_columns):
    mapping = {}
    for col in table_columns:
        if col not in df_columns:
            user_input = input(f"In your CSV file, what column corresponds to '{col}': ").strip()
            mapping[user_input] = col
        else:
            mapping[col] = col
    return mapping


# Function to generate SQL insert statements
def generate_sql_inserts(df, table_name, columns_mapping, engine):
    df = df.rename(columns=lambda x: columns_mapping.get(x.strip(), x))

    # Query the database for existing entries
    existing_entries = pd.read_sql_table(table_name, con=engine)

    # Get the primary key columns for the table
    primary_keys = inspect(engine).get_pk_constraint(table_name)['constrained_columns']

    # Filter out duplicate rows based on primary key columns
    non_duplicate_df = df[~df[primary_keys].apply(tuple,1).isin(existing_entries[primary_keys].apply(tuple,1))]

    # Insert non-duplicate rows into the database
    non_duplicate_df.to_sql(table_name, con=engine, if_exists='append', index=False)





# Database connection
engine = create_engine('mysql+pymysql://root:backend777@35.240.109.106/tastetwister')

# Read CSV files
users_df = read_csv('database_dumps_dec7/user_7dec.csv')
songs_df = read_csv('database_dumps_dec7/songs_7dec.csv')
friend_requests_df = read_csv('database_dumps_dec7/friend_requests_7dec.csv')
friendships_df = read_csv('database_dumps_dec7/friendships_7dec.csv')
blocked_users_df = read_csv('database_dumps_dec7/blocked_users_7dec.csv')

# Define expected columns for each table
users_columns = ['username', 'password', 'token', 'permission']
songs_columns = ['id', 'track_name', 'performer', 'album', 'rating', 'username', 'permission', 'updated_at']
friend_requests_columns = ['id', 'sender', 'receiver', 'status', 'sent_at', 'responded_at']
friendships_columns = ['user1', 'user2']
blocked_users_columns = ['blocker', 'blocked']

# Get column mappings and populate database
users_mapping = get_column_mapping(users_df.columns, users_columns)
generate_sql_inserts(users_df, 'users', users_mapping, engine)

songs_mapping = get_column_mapping(songs_df.columns, songs_columns)
generate_sql_inserts(songs_df, 'songs', songs_mapping, engine)

friend_requests_mapping = get_column_mapping(friend_requests_df.columns, friend_requests_columns)
generate_sql_inserts(friend_requests_df, 'friend_requests', friend_requests_mapping, engine)

friendships_mapping = get_column_mapping(friendships_df.columns, friendships_columns)
generate_sql_inserts(friendships_df, 'friendships', friendships_mapping, engine)

blocked_users_mapping = get_column_mapping(blocked_users_df.columns, blocked_users_columns)
generate_sql_inserts(blocked_users_df, 'blocked_users', blocked_users_mapping, engine)
