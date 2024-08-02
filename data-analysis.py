import requests
import csv
import time
from datetime import datetime

# Replace 'your_api_key' with your actual TMDb API key
api_key = 'your_api_key'
base_url = 'https://api.themoviedb.org/3'
discover_url = f'{base_url}/discover/movie'

# Date range
start_year = 2000
end_date = datetime.now().strftime('%Y-%m-%d')  # Current date

# Function to get movie details from TMDb
def get_movie_details(movie_id):
    url = f'{base_url}/movie/{movie_id}'
    params = {'api_key': api_key}
    response = requests.get(url, params=params)
    return response.json()


# Open a CSV file to write the movie data
with open('top_1000_movies_2000_today.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['id', 'title', 'release_date', 'runtime', 'genres', 'director', 'writers', 'cast', 'overview',
                  'language', 'country', 'vote_average', 'vote_count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    total_movies = 0
    page = 1

    while total_movies < 1000:
        params = {
            'api_key': api_key,
            'sort_by': 'vote_average.desc',
            'primary_release_date.gte': '2000-01-01',
            'primary_release_date.lte': end_date,
            'vote_count.gte': 1000,  # To filter out movies with very few ratings
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

            total_movies += 1

            if total_movies >= 1000:
                break

        page += 1
        time.sleep(0.25)  # Respect rate limits

print('Data extraction complete.')

