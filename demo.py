import MusicClient
c = MusicClient.Client()
c.set_uid() # fill this with uin in your cookie
c.load_cookie("") # fill this with your cookie string on qq music site.
res = c.get_song_fav_playlist(2339472476, "华语热门.csv")
