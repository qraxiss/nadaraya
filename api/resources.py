from api.objects import (Klines, Config, Positions,
                         Balance, Default, Order,
                         WebsocketManage, UserSocketManage,
                         Telegram, MarginConfig, Strategyy, OnOff)
from flask import current_app as app
from flask_restful import Api


api = Api(app)

api.add_resource(OnOff, '/api/onoff')
api.add_resource(Order, '/api/order')
api.add_resource(Config, '/api/config')
api.add_resource(Balance, '/api/balance')
api.add_resource(Default, '/api/default')
api.add_resource(Telegram, '/api/telegram')
api.add_resource(Strategyy, '/api/strategy')
api.add_resource(Positions, '/api/positions')
api.add_resource(MarginConfig, '/api/marginconfig')
api.add_resource(WebsocketManage, '/api/websocket')
api.add_resource(Klines, '/api/klines/<string:pair>')
api.add_resource(UserSocketManage, '/api/usersocket')

