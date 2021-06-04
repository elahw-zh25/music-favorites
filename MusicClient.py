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
        
    def get_playlist_details(self, playlist_id):
        res = self.get_music_api_single_request(playlist_base_url, {"id" : playlist_id})
        return res
        
    def get_song_fav_playlist(self, playlist_id, path = ""):
        playlist_res = self.get_playlist_details(playlist_id)
        playlist_data = playlist_res.json()
        
        if playlist_data["code"] == 0:
            #success data
            song_ids = playlist_data['data']['cdlist'][0]['songids']
            songlist_data = playlist_data['data']['cdlist'][0]['songlist']
            song_list = {}
            for i in range(0, len(songlist_data)):
                song_id = songlist_data[i]['id']
                song_name = songlist_data[i]['name']
                singers = songlist_data[i]['singer']
                singer_names = []
                for j in range(0, len(singers)):
                    singer_names.append(singers[j]['name'])
                song_list[song_id] = {"name" : song_name, "singers" : singer_names}
                
            check_fav_res = self.get_song_fav_count(list(song_list.keys()))
            fav_data = check_fav_res.json()
            out_str = "Song\tSinger\tFav Count\n"
            if fav_data['req_0']['code'] == 0:
                # success
                fav_nums = fav_data['req_0']['data']['m_numbers']
                for k in song_list.keys():
                    out_str += "%s\t%s\t%s\n"%(song_list[k]['name'], "&".join(song_list[k]['singers']), fav_nums[str(k)])
                    song_list[k]['fav'] = fav_nums[str(k)]

                print(out_str)

            if path != "":
                f_o = open(path, 'w')
                f_o.write(out_str)
                f_o.close()
