from data.access import get_default, get_config, get_values
from logic import get_step_info, get_balance
from flask_restful import Resource, request
from binance.client import Client
from logic import WebSocket


class ApiResources:
    positions = {}
    strategy = {}
    klines = {}

    default = get_default()
    config = get_config()
    values = get_values()

    run = config['run']

    client = Client(**default['account'])
    websocket = WebSocket(client, default['account'])

    step_info = get_step_info(client)
    balance = get_balance(client)


class BaseApi(Resource):
    def __init__(self) -> None:
        super().__init__()
        try:
            self.data = request.json
        except:
            self.data = None
        self.json = {}
        self.resources = ApiResources()
        31
        31
