from threading import Thread
import binance
import asyncio


from logic.exchange.streams.helpers import kline_update, account_update, order_update
from helpers import socket_parser
from api import request


class WebSocket:
    def __init__(self, client, account) -> None:
        self.client = client
        self.sockets = dict()
        self.account = account

        self.updates = {
            'ORDER_TRADE_UPDATE': order_update,
            'ACCOUNT_UPDATE': account_update
        }

    async def kline_async(self, socket: str, limit: int = 40):
        symbol, interval = socket_parser(socket)
        klines = self.client.futures_klines(
            symbol=symbol, interval=interval, limit=limit)
        value = request('/klines', 'post',
                        value=f'/{socket}', json=klines)
        async_client = await binance.AsyncClient.create()
        bm = binance.BinanceSocketManager(async_client)
        ts = bm.futures_multiplex_socket(streams=[socket])
        self.sockets[socket] = True
        async with ts as tscm:
            try:
                while self.sockets[socket]:
                    res = await tscm.recv()
                    kline_update(res)
            except:
                pass

        await async_client.close_connection()

    def kline(self, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.kline_async(**kwargs))
        loop.close()

    def kline_thread(self, **kwargs):
        Thread(target=self.kline, kwargs=kwargs).start()

    def kline_close(self, socket: str):
        if self.sockets[socket]:
            self.sockets[socket] = False
            del self.sockets[socket]

    async def user_async(self, account):
        async_client = await binance.AsyncClient.create(**account)
        bm = binance.BinanceSocketManager(async_client)
        ts = bm.futures_user_socket()

        self.sockets['user'] = True
        async with ts as tscm:
            while self.sockets['user']:
                res = await tscm.recv()
                try:
                    Thread(target=self.updates[res['e']], args=(res,)).start()
                except KeyError:
                    pass

        await async_client.close_connection()

    def user(self, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.user_async(**kwargs))
        loop.close()

    def user_thread(self, **kwargs):
        Thread(target=self.user, kwargs=kwargs).start()

    def user_close(self):
        if self.sockets['user']:
            self.sockets['user'] = False


    def get_sockets(self):
        return list(self.sockets)