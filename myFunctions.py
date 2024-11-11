import pandas as pd
import numpy as np
import requests
import pickle
import os

class recomender:
  def __init__(self, path_):
    try:
        models =pickle.load(open(path_,'rb'))
        #collaborativ_model
        self.X = models['X']
        self.W = models['W']
        self.B = models['B']
        self.model1 = models['model']
        self.movie_pivot = models['pivot']
    except:
        print('Problem with loading recommender data+++++++++++++++++++')
  
  def recomend_content_based(self, m_id):
    #It returns the movieId of recommended movie
    indx = list(self.movie_pivot.index).index(m_id)
    _,suggesion = self.model1.kneighbors(self.movie_pivot.iloc[indx].values.reshape(1,-1), n_neighbors = 30)
    return list(self.movie_pivot.index[suggesion[0]])

  def recomend_collab_based(self, user_indx):
    #It has to return the recommended movieId based on user_indx
    #userIndx is column_number in movie_pivot table
    pred = np.dot(self.X, self.W.T) + self.B
    indx = np.argsort(-pred[:,user_indx])[:30]
    #indx is simple index representing row number in movie_pivot 
    return list(self.movie_pivot.index[indx])
  
  def get_user_indx(self, user_id):
    users = list(self.movie_pivot.columns)
    return users.index(user_id)





class avl_titles:
  def __init__(self):
    try:
      self.titles = pickle.load(open('MovieRecommenderWeb/static/titles','rb'))
    except:
       self.titles = {'title':None}
  
  def get_titles(self):
     return self.titles['title']





class Movie:
  def __init__(self, path_):
    try:
        data_table = pd.read_csv(path_, low_memory=False)
        self.data_table = data_table
    except:
        columns = ['title', 'vote_average', 'vote_count', 'status', 'release_date',
       'revenue', 'runtime', 'adult', 'backdrop_path', 'budget', 'homepage',
       'imdb_id', 'original_language', 'original_title', 'overview',
       'popularity', 'poster_path', 'tagline', 'genres',
       'production_companies', 'production_countries', 'spoken_languages',
       'keywords']        
        df = pd.DataFrame(columns=columns)
        self.data_table=df
        print('Problem with loading Movie data+++++++++++++++++++')
        
  def get_id(self, title):
    #It returns index(row number) and movieId of give title
    try:
      indx = self.data_table['title']==title
      lst = []
      lst.append(list(self.data_table.loc[indx,'id'].index)[0])
      lst.append(list(self.data_table.loc[indx,'id'])[0])
      return lst
    except:
       return [9615,16]

  def get_indices(self, lst_m_id):
    indx = self.data_table['id'].isin(lst_m_id)
    return (list(self.data_table.loc[indx,'id'].index))

  def movie_details(self, movie_id):
    try:
      da = self.data_table.loc[movie_id]

      data={'adult': da['adult'],
            'title': da['title'],
            'language': da['original_language'],
            'poster_path': 'https://image.tmdb.org/t/p/original'+ str(da['poster_path']),
            'backdrop_path': 'https://image.tmdb.org/t/p/w1280'+ str(da['backdrop_path']),
            'release_date': da['release_date'],
            'overview': da['overview'],
            'average_rating': da['vote_average'].round(1),
            'vote_count': da['vote_count'],
            'genre': da['genres'],
            'runtime': da['runtime'],
            'production_countries': da['production_countries']
          }
      return data
    
    except IndexError:
      return None
      print('No data retrived')
 
  def get_popular_list(self):
    try:
      data = self.data_table.sort_values(by=['popularity'], ascending=[False]).iloc[0:20].index
      return data
    except IndexError:
      print('List not found +++++++++++++++++++++++')
      return None





class crew_cast:
    def __init__(self, path_):
        try:
            table = pd.read_csv(path_, low_memory=False)
            self.table = table
        except:
            columns = ['id','cast','crew']
            df = pd.DataFrame(columns=columns)
            self.table = df
            print('Problem with loading credits data+++++++++++++++++++')
    
    def get_crew(self, movie_id):
        try:
            return eval((self.table.loc[self.table['id']==movie_id, 'crew']).values[0])
        except Exception:
            return [{'name':None,'job':None}]
        
    def get_cast(self, movie_id):
        try:
            return eval((self.table.loc[self.table['id']==movie_id,'cast']).values[0])
        except Exception:
            return [{'name':None,'character':None}]





class streaming:
  def __init__(self):
    url = "https://api.themoviedb.org/3/movie/now_playing?language=en-US&page=1"
    token = os.getenv('token')
   
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer"+ " " + token
      }
    self.response = requests.get(url, headers=headers)

  def get_streming_now(self):
    return self.response.json()['results'][0:5]




def get_video(movie_id):
    try:
      url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?language=en-US"   
      f = open('MovieRecommenderWeb/static/token.txt','r')
      token = f.read()
      headers = {
        "accept": "application/json",
        "Authorization": "Bearer"+" "+token
      }
      response = requests.get(url, headers=headers)
      video_data = []
      lst = response.json()['results']
      for value in lst:
        video_data.append({'name':value['name'], 'lnk':'https://www.youtube.com/embed/'+value['key']})
      return video_data
    except:
       return [{'name':'Video not found! Call limit exceeded!', 'lnk':'https://www.youtube.com/embed/0tLi7k9feZc?si=43ps8vA3OIHdzQSP'}]

def get_credits(m_id):
  try:
    url = f"https://api.themoviedb.org/3/movie/{m_id}/credits?language=en-US"
    f = open('MovieRecommenderWeb/static/token.txt','r')
    token = f.read()
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer"+ " " + token
      }
    response = requests.get(url, headers=headers)
    return {'cast':response.json()['cast'], 'crew': response.json()['crew']}
  except:
     return None
