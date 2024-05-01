from flask import Flask, render_template, request # type: ignore
from myFunctions import Movie, crew_cast, recomender,avl_titles, get_video, get_credits


movie_data = Movie('MovieRecommenderWeb/IMBD_Movie_data/tmdb_data_small1.csv')
cast_crew_data = crew_cast('MovieRecommenderWeb/IMBD_Movie_data/credits.csv')
recomender_ = recomender('MovieRecommenderWeb/static/Recomender')
avl_title = avl_titles()



app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    #Get user index
    try:
        user_indx = int(request.args.get("userId"))
        print(user_indx)
    except:
        user_indx = 11
    #user_indx = 6 #It can change based on user login.

    popular_id = movie_data.get_popular_list()
    recommended_movie = recomender_.recomend_collab_based(user_indx)

    indices = movie_data.get_indices(recommended_movie)
    recomended_movie = []
    for indx in indices:
        recomended_movie.append(movie_data.movie_details(indx) if movie_data.movie_details(indx) is not None else None)

    popular_movie = []
    for m_id in popular_id:
        popular_movie.append(movie_data.movie_details(m_id))
    
    return render_template('index.html', popular_movie=popular_movie, collab_recommendation=recomended_movie, user = user_indx)



@app.route('/found', methods=['POST'])
def found():
    #Based on search input, find movie id
    title = request.form.get("title")
    #print(title)
    m_id = movie_data.get_id(title)
    #x/Based on data posted by form, find and make data of searched movie.
    recomended_movie_ids = recomender_.recomend_content_based(m_id[1])
    indices = movie_data.get_indices(recomended_movie_ids)
    
    recomended_movie = []
    for indx in indices:
        recomended_movie.append(movie_data.movie_details(indx) if movie_data.movie_details(indx) is not None else None)
    return render_template('found.html', data = recomended_movie)


@app.route('/movies/<title>', methods=['GET'])
def show_movie(title):
    m_id = movie_data.get_id(title)

    credits = get_credits(m_id[1])
    if credits == None:
        data = {'movie': movie_data.movie_details(m_id[0]),
                'cast': cast_crew_data.get_cast(m_id[1]),
                'crew': cast_crew_data.get_crew(m_id[1]),
                'videos': get_video(m_id[1])
                }
    else:
        data = {'movie': movie_data.movie_details(m_id[0]),
                'cast': credits['cast'],
                'crew': credits['crew'],
                'videos': get_video(m_id[1])
                }
    return render_template('movie.html', data=data)



if __name__ == '__main__':
    app.run(debug=True)