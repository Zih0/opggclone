# python code
from flask import Flask, render_template, request
import os
import requests
from pprint import pprint as pp

app = Flask(__name__)

apikey = 'RGAPI-7d804e48-520f-463e-bdbd-7a6c5189bf1b'
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
    encrypted_id = res.json()['id']
    url_league = "https://kr.api.riotgames.com/lol/league/v4/entries/by-summoner/{}".format(encrypted_id)
    res_league = requests.get(url=url_league, headers=headers)
    league_dicts = res_league.json()

    pp(league_dicts)
    print('-------------------------------')
    def get_league_info(league_dict):
        res = [
            league_dict.get('queueType'),
            league_dict.get('tier'),
            league_dict.get('rank'),
            league_dict.get('wins'),
            league_dict.get('losses'),
            league_dict.get('leagueName'),
            league_dict.get('leaguePoints')
        ]
        return res

    results = []
    for league_dict in league_dicts:
        results.append(get_league_info(league_dict))
    print(results)
    length = len(results)

    return render_template('search.html', sum_name=sum_name, results=results, length=length)


