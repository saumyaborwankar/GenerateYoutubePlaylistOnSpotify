import requests
import json
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import requests
import youtube_dl

username=""
spotify_token=""

#curl -X GET "https://api.spotify.com/v1/search?q=tania%20bowra&type=artist" -H "Authorization": "Bearer {}".format(spotify_token)
query="https://api.spotify.com/v1/search/?q='YT&20playlist'&type=playlist"
response=requests.get(query,headers={
        "Authorization":"Bearer {}".format(spotify_token)
        })
#final_dict={}

response_json=response.json()
for i in response_json['playlists']['items']:
    if i['owner']['id']==username:
        playlist_id=i['uri']
        break
'''
if len(playlist_id)==0:
    playlis=playlist()
    playlis_id=playlis.create_playlist()'''
class playlist:
    def __init__(self):
        self.youtube_client = self.get_youtube_client()
        self.final_dict={}
        
    def create_playlist():
        
        ply_data=json.dumps({
            "name":"YT playlist",
            "description":"All liked yt videos",
            "public":True
            })
        query="https://api.spotify.com/v1/users/{}/playlists".format(username)
        respons=requests.post(
            query,
            data=ply_data,
            headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
                })
        response_json=respons.json()
        playlist_id=response_json['id']
        return playlist_id
    
    #### Search for song #####
    def get_uri(self,song_name,artist):
        query2="https://api.spotify.com/v1/search?q=track%20{}+artist%3A{}&type=track&type=artist".format(song_name,artist)
        response2=requests.get(query2, headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
                })
        response2_json=response2.json()
        
        uris=response2_json['artists']['items'][0]['uri']
        return uris
    #### CODE MADE POSSIBLE WITH THE HELP OF GOOGLE ######
    def addSong(self):
        self.LikedVideos()
        uris=[info['spotify_id'] for song,info in final_dict.items()]
        #uris=["spotify:track:4iV5W9uYEdYUVa79Axb7Rh"]
        
        uri_json=json.dumps(uris)
        if len(playlist_id)==0:
            playlist_id=self.create_playlist()
        query3 = "https://api.spotify.com/v1/playlists/{}/tracks".format(
                    playlist_id)
        response3=requests.post(query3,data=uri_json,headers={
                "Content-Type":"application/json",
                "Authorization":"Bearer {}".format(spotify_token)
                })
        if response3.status_code != 200:
            raise ResponseException(response.status_code)
    
        response3_json = response3.json()
        return response3_json
    ### CODE TAKEN FROM YOUTUBE API DOCUMENTATION #######
    def YTclient(self):
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    
        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"
    
        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()
    
        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)
    
        return youtube_client
    
    def LikedVideos(self):
        yt_client=YTclient()
        request=yt_client.videos().list(
            part='snippet,contentDetails,statistics',
            myRating='like')
        response=request.execute()
        #### GET INFO FROM VIDEO ###
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "https://www.youtube.com/watch?v={}".format(
                item["id"])
    
            # use youtube_dl to collect the song name & artist name
            video = youtube_dl.YoutubeDL({}).extract_info(
                youtube_url, download=False)
            song_name = video["track"]
            artist = video["artist"]
    
            if song_name is not None and artist is not None:
                # save all important info and skip any missing song and artist
                self.final_dict[video_title] = {
                    "youtube_url": youtube_url,
                    "song_name": song_name,
                    "artist": artist,
    
                    # add the uri, easy to get song to put into playlist
                    "spotify_uri": self.get_uri(song_name, artist)
    
                }

if __name__ == 'main':
    create=playlist()
    create.addSong()
