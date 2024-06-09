from flask import Flask, render_template, request
import pickle
import requests

app = Flask(__name__)

def fetch_poster(movie_id):
    api_key = '9dfb521989eb5055d78db120b6b3ad9a'
    base_url = "https://api.themoviedb.org/3/movie/"
    url = f"{base_url}{movie_id}?api_key={api_key}&language=en-US"
    fallback_url = "https://via.placeholder.com/500x750?text=No+Poster+Available"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}"
            return full_path
        else:
            return fallback_url
    except requests.exceptions.RequestException:
        return fallback_url

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters

# Load pre-trained data
movies = pickle.load(open('./model/movie_list.pkl', 'rb'))
similarity = pickle.load(open('./model/similarity.pkl', 'rb'))

@app.route('/', methods=['GET', 'POST'])
def index():
    movie_list = movies['title'].values
    recommended_movie_names = []
    recommended_movie_posters = []
    selected_movie = None
    
    if request.method == 'POST':
        selected_movie = request.form['movie']
        recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    
    return render_template('index.html', movie_list=movie_list, recommended_movie_names=recommended_movie_names, recommended_movie_posters=recommended_movie_posters, selected_movie=selected_movie)

app.jinja_env.globals.update(zip=zip)

if __name__ == '__main__':
    app.run(debug=True)
