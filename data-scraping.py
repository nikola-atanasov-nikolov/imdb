import requests
import csv
import time
from datetime import datetime
import os

# Replace 'your_api_key' with your actual TMDb API key
api_key = 'fb2e3a8285e168cda3a42b70434becfc'
base_url = 'https://api.themoviedb.org/3'
discover_url = f'{base_url}/discover/movie'

now = datetime.now()
current_date = now.strftime("%Y-%m-%d")

# Define the file name
filename = 'dates.csv'

# Check if the file exists and if it is empty
file_exists = os.path.isfile(filename)
file_is_empty = not file_exists or os.path.getsize(filename) == 0

# Open the CSV file in append mode
with open(filename, mode='a', newline='') as file:
    writer = csv.writer(file)

    # If the file is empty, write January 1, 2000
    if file_is_empty:
        writer.writerow(['2024-07-31'])


with open(filename, mode='r') as file:
    reader = csv.reader(file)
    rows = list(reader)
    if rows:
        last_date = rows[-1][0]  # Get the last date in the file

print(last_date)

# Date range
start_year = last_date
end_date = datetime.now().strftime('%Y-%m-%d')  # Current date

print(start_year)
print(end_date)


# Function to get movie details from TMDb
def get_movie_details(movie_id):
    url = f'{base_url}/movie/{movie_id}'
    params = {'api_key': api_key}
    response = requests.get(url, params=params)
    return response.json()


# Check if the movie CSV file exists and if it has headers
headers_exist = os.path.isfile('top_100_movies_2024_today.csv') and os.path.getsize('top_100_movies_2024_today.csv') > 0

# Open the CSV file to write movie data
with open('top_100_movies_2024_today.csv', mode='a', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'title', 'release_date', 'runtime', 'genres', 'director', 'writers', 'cast', 'overview',
                  'language', 'country', 'vote_average', 'vote_count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write header if file is empty
    if not headers_exist:
        writer.writeheader()

    page = 1

    while True:
        params = {
            'api_key': api_key,
            'sort_by': 'vote_average.desc',
            'primary_release_date.gte': start_year,
            'primary_release_date.lte': end_date,
            'page': page
        }
        response = requests.get(discover_url, params=params)
        data = response.json()

        if 'results' not in data or not data['results']:
            break

        for movie in data['results']:
            movie_details = get_movie_details(movie['id'])
            genres = ', '.join([genre['name'] for genre in movie_details.get('genres', [])])
            director = ''
            writers = ''
            cast = ''

            # Fetching credits
            credits_url = f'{base_url}/movie/{movie["id"]}/credits'
            credits_response = requests.get(credits_url, params=params)
            credits_data = credits_response.json()

            if 'crew' in credits_data:
                director = ', '.join([member['name'] for member in credits_data['crew'] if member['job'] == 'Director'])
                writers = ', '.join(
                    [member['name'] for member in credits_data['crew'] if member['department'] == 'Writing'])

            if 'cast' in credits_data:
                cast = ', '.join([member['name'] for member in credits_data['cast'][:5]])  # Top 5 cast members

            writer.writerow({
                'id': movie_details['id'],
                'title': movie_details['title'],
                'release_date': movie_details['release_date'],
                'runtime': movie_details['runtime'],
                'genres': genres,
                'director': director,
                'writers': writers,
                'cast': cast,
                'overview': movie_details['overview'],
                'language': movie_details['original_language'],
                'country': movie_details['production_countries'][0]['name'] if movie_details[
                    'production_countries'] else '',
                'vote_average': movie_details['vote_average'],
                'vote_count': movie_details['vote_count']
            })

        page += 1
        time.sleep(0.25)  # Respect rate limits


# Open the CSV file in append mode
with open(filename, mode='a', newline='') as file:
    writer = csv.writer(file)

    # Write the current date to the file
    writer.writerow([current_date])

print(f"Date {current_date} written to {filename}")


