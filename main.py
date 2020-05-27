# python code
from flask import Flask, render_template, request
import os
import requests
from pprint import pprint as pp

app = Flask(__name__)

apikey = 'RGAPI-526e0d18-9d1d-4b2d-bf5a-833665ba684c'
print("api_key\n", apikey)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search')
def search():
    sum_name = request.args.get('name')
    url = "https://kr.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}".format(sum_name)
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": apikey
}
    res = requests.get(url=url, headers=headers)
    account_id = res.json()['accountId']
    encrypted_id = res.json()['id']
    url_league = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(encrypted_id)
    res_league = requests.get(url=url_league, headers=headers)
    league_dicts = res_league.json()

    def get_league_info(league_dict):
        res = [
            league_dict.get('queueType'),
            league_dict.get('tier'),
            league_dict.get('rank'),
            league_dict.get('wins'),
            league_dict.get('losses'),
            league_dict.get('leaguePoints'),
            round(100*league_dict.get('wins')/(league_dict.get('losses')+league_dict.get('wins')))
        ]
        return res

    results = []
    for league_dict in league_dicts:
        results.append(get_league_info(league_dict))

    print(results)
    length = len(results)




    url_GameID = "https://kr.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?queue=420".format(
        account_id)  # {encryptedAccountId} = account_ID
    # 매치를 못찾을 경우

    res_GameID = requests.get(url=url_GameID, headers=headers)

    Matches = res_GameID.json()['matches']  # gameID가 들어있는 Mathes를 가져옴
    # 매치 20개로 자르기
    Matches = Matches[:20]

    Game_IDs = []
    for Matche in Matches:
        Game_IDs.append(Matche['gameId'])

    champID = []  # 챔프
    Game_DATAs = []
    static_data_url = 'http://ddragon.leagueoflegends.com/cdn/9.24.2/data/en_US/champion.json'
    champdata = requests.get(static_data_url).json()
    champdata = champdata['data']
    champname = []
    for Game_ID in Game_IDs:

        Game_DATA = {'game_time': '', 'b_win': '', 'b_towerKills': '', 'b_inhibitorKills': '', 'b_baronKills': '',
                     'b_riftHeraldKills': '',
                     'r_win': '', 'r_towerKills': '', 'r_inhibitorKills': '', 'r_baronKills': '',
                     'r_riftHeraldKills': '',
                     'b_player': [], 'r_player': [], 'stats': '', 'champ_name': ''}

        url_GameData = "https://kr.api.riotgames.com/lol/match/v4/matches/{}".format(Game_ID)
        res_GameData = requests.get(url=url_GameData, headers=headers)
        # 플레이시간
        Game_DATA['game_time'] = res_GameData.json()['gameDuration']

        # 팀정보
        teams = res_GameData.json()['teams']

        blue = teams[0]
        red = teams[-1]
        if (blue['win'] == 'Win'):
            Game_DATA['b_win'] = '승리'
            Game_DATA['r_win'] = '패배'
        else:
            Game_DATA['b_win'] = '패배'
            Game_DATA['r_win'] = '승리'

        Game_DATA['b_towerKills'] = blue['towerKills']  # 포탑
        Game_DATA['b_inhibitorKills'] = blue['inhibitorKills']  # 억제기
        Game_DATA['b_baronKills'] = blue['baronKills']  # 바론
        Game_DATA['b_riftHeraldKills'] = blue['riftHeraldKills']  # 전령

        Game_DATA['r_towerKills'] = red['towerKills']  # 포탑
        Game_DATA['r_inhibitorKills'] = red['inhibitorKills']  # 억제기
        Game_DATA['r_baronKills'] = red['baronKills']  # 바론
        Game_DATA['r_riftHeraldKills'] = red['riftHeraldKills']  # 전령

        # 최근 5회 데이터
        game_5 = res_GameData.json()['participantIdentities']
        myid_num = 0
        # blue, red 플레이어 이름
        for i in range(0, 10):
            if account_id == game_5[i].get('player').get('accountId'):
                myid_num = i
            if i < 5:
                Game_DATA['b_player'] += [game_5[i].get('player').get('summonerName')]
            else:
                Game_DATA['r_player'] += [game_5[i].get('player').get('summonerName')]





        # 개인 통계
        participants = res_GameData.json()['participants'][myid_num]
        champID.append(participants['championId'])
        stats = participants['stats']
        Game_DATA['stats'] = stats
        Game_DATAs.append(Game_DATA)

        for mychamp in champID:
            for key, value in champdata.items():
                if int(mychamp) == int(value['key']):
                   Game_DATA['champ_name'] = value['name']





#최근 5회 챔피언



    pp(Game_DATAs)
    print(champname)


    return render_template('search.html', sum_name=sum_name, results=results, length=length,champname=champname, Game_DATAs=Game_DATAs, zip=zip)


if __name__ == '__main__':
    app.run(host='127.0.0.1')