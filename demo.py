import MusicClient
c = MusicClient.Client()

c.get_song_info_playlist(7772286665, "华语经典.tsv")

#c.set_uid() # fill this with uin in your cookie
#c.load_cookie("") # fill this with your cookie string on qq music site.
#c.get_top_singers_play_count(50, "top50歌手播放量查询.tsv")
