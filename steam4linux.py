from flask import Flask
from flask import render_template
from flask import request
from xml.etree import ElementTree

import json
import requests

app = Flask(__name__)

@app.route('/')
def index():
        return render_template('index.html')

@app.route('/hello/')
@app.route('/hello/<name>')
def hello(name=None):
        return render_template('hello.html', name=name)

@app.route('/search/', methods=['POST'])
def search():
        STEAM_API_KEY = '832A70A00780C68A106067A713923817'

        def get_steamid(username):
            community_url = 'https://steamcommunity.com/id/' + username + '/?xml=1'
            response = requests.get(community_url)

            root = ElementTree.fromstring(response.content)
            return root.find('steamID64').text

        def get_owned_games(steamid):
            steamapi_service = 'IPlayerService'
            steamapi_api = 'GetOwnedGames'
            steamapi_version = 'v0001'

            steamapi_url = 'http://api.steampowered.com/' + \
                steamapi_service + '/' + steamapi_api + '/' + steamapi_version + \
                '/?key=' + STEAM_API_KEY + '&steamid=' + steamid  + '&format=json'
            response = requests.get(steamapi_url)

            return response.json()

        def get_games_by_user(steamid):
            owned_games = get_owned_games(steamid)
            idx = 1
            for app in owned_games['response']['games']:
                appid = str(app['appid'])
                store_url = 'http://store.steampowered.com/api/appdetails/?' + \
                    'appids=' + appid + '&cc=BR&v=1'

                response = requests.get(store_url)
                game = response.json()
                if game[appid]['success']:
                    game[appid]['data']['idx'] = idx
                    idx = idx + 1
                    yield game[appid]['data']

        username = request.form['username']
        steamid = get_steamid(username)
        print('steamID64: ' + steamid)

        game_list = get_games_by_user(steamid)

        context = { 'username': username, 'game_list': game_list }

        return render_template('results.html', rsp=context)
