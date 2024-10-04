# save this as app.py
from flask import Flask, request, render_template, request
import pickle
import requests
import pandas as pd
from patsy import dmatrices

movies = pickle.load(open('model/movies_list.pkl', 'rb'))
similarity = pickle.load(open('model/similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse= True, key=lambda x: x[1])
    recommended_movies_name = []
    recommended_movies_poster = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i[0]].title)

    return recommended_movies_name, recommended_movies_poster

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/recommendation', methods = ['GET', 'POST'])
def recommendation():
    movie_list = movies['title'].values
    status = False
    if request.method == "POST":
        try:
            if request.form:
                movies_name = request.form['movies']
                print(movies_name)
                recommended_movies_name, recommended_movies_poster = recommend(movies_name)
                print(recommended_movies_name)
                print(recommended_movies_poster)
                status = True

                return render_template("prediction.html", movies_name = recommended_movies_name, poster = recommended_movies_poster, movie_list = movie_list, status = status)




        except Exception as e:
            error = {'error': e}
            return render_template("prediction.html",error = error, movie_list = movie_list, status = status)

    else:
        return render_template("prediction.html", movie_list = movie_list, status = status)


@app.route('/movie_overview/<movie_name>')
def movie_overview(movie_name):
    df=pd.read_csv('Dataset/tmdb_5000_credits.csv')
    df1=pd.read_csv('Dataset/tmdb_5000_movies.csv')
    movie_info = df[df['title'] == movie_name]  # Use 'original_title' column
    movie_info1=df1[df1['original_title']==movie_name]
    
    if not movie_info.empty:
        director = movie_info['crew'].values[0]  # Adjust 'crew' to your actual column name
        overview = movie_info1['overview'].values[0]  # Adjust 'overview' to your actual column name
        rating = movie_info1['vote_count'].values[0]  # Adjust 'rating' to your actual column name
        poster = fetch_poster(19995)  # Adjust 'poster_path' to your actual column name
        
        return render_template('movie_overview.html', title=movie_name, director=director, overview=overview, rating=rating, poster=poster)
    else:
        return "Movie not found.", 404

# Keep the existing routes...


    






if __name__ == '__main__':
    app.debug = True
    app.run()
    