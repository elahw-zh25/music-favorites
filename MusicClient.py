'''
  Copyright [2021] [elahw-zh25]

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
'''
import requests
import json
import time

base_url = "https://u.y.qq.com/cgi-bin/musicu.fcg"
playlist_base_url = "https://c.y.qq.com/v8/fcg-bin/fcg_v8_playlist_cp.fcg"

class Client():
    def __init__(self, uid = 0, cookies = {}):
        # set up cookies and headers
        self.uid = uid
        self.cookies = cookies
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
        
    def set_uid(self, uid):
        self.uid = uid
        
    def load_cookie(self, cookie_str):
        cookie_list = cookie_str.split(';')
        cookies = {}
        for c in cookie_list:
            c = c.strip()
            kv = c.split('=', 1)
            cookies[kv[0]] = kv[1]
        self.cookies = cookies
        
    def get(self, url, params = None):
        res = requests.get(url, params = params, headers = self.headers, cookies = self.cookies)
        return res
        
    def post(self, url, post_data):
        res = requests.post(url, data = post_data, headers = self.headers, cookies = self.cookies)
        return res
    
    def get_music_api(self, module, method, param):
        actual_param = {"uin":str(self.uid)}
        actual_param.update(param)
        get_data = {"comm": {"uin":str(self.uid)}, "req_0":{"module": module, "method":method, "param":actual_param}}
        final_url = base_url + "?&data=" + json.JSONEncoder().encode(get_data)
        return self.get(final_url)
        
    def get_music_api_single_request(self, url, params):
        actual_param = {"uin":str(self.uid), "format":"json", "inCharSet" : "utf-8", "outCharSet":"utf-8", "newsong" : 1}
        actual_param.update(params)
        res = self.get(url, params=actual_param)
        return res
    
    def post_music_api(self, module, method, param):
        actual_param = {"uin":str(self.uid)}
        actual_param.update(param)
        post_data = {"req_0":{"module": module, "method":method, "param":actual_param}}
        return self.post(base_url, post_data)
    
    # sont_id_list : int[]
    def get_song_fav_count(self, song_id_list):
        return self.get_music_api("music.musicasset.SongFavRead", "GetSongFansNumberById", {"v_songid" : song_id_list})
    
    # sont_mid_list : string[]
    def get_song_play_count(self, song_mid_list):
        return self.get_music_api("music.musicToplist.PlayTopInfoServer", "GetPlayTopData", {"songMidList" : song_mid_list})
    
    # return top 80 singers in singer hall with mid info
    def get_top_singers(self, extra_params = {}):
        default_params = {"area":-100, "index":-100, "sex":-100, "genre":-100, "cur_page":1, "sin":0}
        default_params.update(extra_params)
        return self.get_music_api("music.musichallSinger.SingerList", "GetSingerListIndex", default_params)
    
    # get top songs of the singer
    def get_song_list(self, singer_mid, start = 0, page_size = 10):
        params = {"singerMid":singer_mid, "begin":start, "num":page_size, "order":1}
        return self.get_music_api("musichall.song_list_server", "GetSingerSongList", params)
    
    # get song total play count of singer
    def get_song_play_singer(self, singer_mid, path = "", top_songs = 100):
        song_list = {}
        
        list_res = self.get_song_list(singer_mid, 0, top_songs)
        data = list_res.json()
        if (data['req_0']['code'] == 0):
            song_list_data = data['req_0']['data']['songList']
            for song in song_list_data:
                song_mid = song['songInfo']['mid']
                song_name = song['songInfo']['name']
                singers = song['songInfo']['singer']
                singer_names = []
                for singer in singers:
                    singer_names.append(singer['name'])
                song_list[song_mid] = {"name" : song_name, "singers" : singer_names, "play" : "0w+"}
        
        list_mid = list(song_list.keys())
        fixSizeChunk = 10
        for i in range(0, len(list_mid), fixSizeChunk):
            check_play_res = self.get_song_play_count(list_mid[i:i + fixSizeChunk])
            play_data = check_play_res.json()
            if play_data['req_0']['code'] == 0:
                play_nums = play_data['req_0']['data']['data']
                
                # early return heuristic that no more hot songs after this chunk
                if len(play_nums.keys()) == 0:
                    break
                for mid in play_nums.keys():
                    song_list[mid]['play'] = play_nums[mid]['listenCnt']
            time.sleep(1)

        out_str = "Song\tSinger\tPlay Count(w+)\n"
        total_count = 0
        for song_id in song_list.keys():
            out_str += "%s\t%s\t%s\n"%(song_list[song_id]['name'], "&".join(song_list[song_id]['singers']), song_list[song_id]['play'][:-2])
            total_count += int(song_list[song_id]['play'][:-2])

        # print(out_str)
        if path != "":
            f_o = open(path, 'w')
            f_o.write(out_str)
            f_o.close()
        
        print("Total play count: %s w+"%total_count)
        return total_count
        
    def get_top_singers_play_count(self, start = 0, size = 10):
        singer_list = {}
        singers_res = self.get_top_singers()
        singers_data = singers_res.json()
        if singers_data['req_0']['code'] == 0:
            singer_list_data = singers_data['req_0']['data']['singerlist']
            for i in range(start, min(start + size, len(singer_list_data))):
                singer_info = singer_list_data[i]
                singer_list[singer_info['singer_mid']] = {"name" : singer_info['singer_name']}
                singer_list[singer_info['singer_mid']]['play'] = self.get_song_play_singer(singer_info['singer_mid'])
                
        out_str = "Singer\tPlay Count(w+)\n"
        for singer_mid in singer_list:
            out_str += "%s\t%s\n"%(singer_list[singer_mid]['name'], singer_list[singer_mid]['play'])
        print(out_str)
        
    def get_playlist_details(self, playlist_id):
        res = self.get_music_api_single_request(playlist_base_url, {"id" : playlist_id})
        return res
        
    def get_song_info_playlist(self, playlist_id, path = ""):
        playlist_res = self.get_playlist_details(playlist_id)
        playlist_data = playlist_res.json()
        song_list = {}
        song_mid_list = {}
        
        if playlist_data["code"] == 0:
            #success data
            song_ids = playlist_data['data']['cdlist'][0]['songids']
            songlist_data = playlist_data['data']['cdlist'][0]['songlist']
            for i in range(0, len(songlist_data)):
                song_id = songlist_data[i]['id']
                song_mid = songlist_data[i]['mid']
                song_mid_list[song_mid] = song_id
                song_name = songlist_data[i]['name']
                singers = songlist_data[i]['singer']
                singer_names = []
                for j in range(0, len(singers)):
                    singer_names.append(singers[j]['name'])
                song_list[song_id] = {"name" : song_name, "singers" : singer_names, "mid" :song_mid, "play":"0"}
                
            check_fav_res = self.get_song_fav_count(list(song_list.keys()))
            fav_data = check_fav_res.json()

            if fav_data['req_0']['code'] == 0:
                # success
                fav_nums = fav_data['req_0']['data']['m_numbers']
                for song_id in song_list.keys():
                    song_list[song_id]['fav'] = fav_nums[str(song_id)]

            list_mid = list(song_mid_list.keys())
            fixSizeChunk = 10
            for i in range(0, len(list_mid), fixSizeChunk):
                check_play_res = self.get_song_play_count(list_mid[i:i + fixSizeChunk])
                play_data = check_play_res.json()
                if play_data['req_0']['code'] == 0:
                    play_nums = play_data['req_0']['data']['data']
                    for mid in play_nums.keys():
                        song_list[song_mid_list[mid]]['play'] = play_nums[mid]['listenCnt']
                time.sleep(1)
            
            out_str = "Song\tSinger\tFav Count\tPlay Count(w+)\n"
            for song_id in song_list.keys():
                    out_str += "%s\t%s\t%s\t%s\n"%(song_list[song_id]['name'], "&".join(song_list[song_id]['singers']), song_list[song_id]['fav'], song_list[song_id]['play'][:-2])
            print(out_str)

            if path != "":
                f_o = open(path, 'w')
                f_o.write(out_str)
                f_o.close()
