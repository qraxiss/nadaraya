def err_return(err_class:str):
    return err_class.replace("<class '", '').replace("'>", '')

def telegram_message_formatter(order_type: str, order: dict) -> str:
    if order_type != None:
        text = f"""
                    symbol:{order['s']}\n
                    market:{order['ot']}\n
                    last price:{order['ap']}\n
                    position volume:{order['ap']*order['q']}
                    """

        if order_type == 'NEW':
            before = "New Position!\n"
            after = ""
        elif order_type == 'CLOSE':
            before = "Closed Position\n"
            after = f"\nprofit:{order['rp']}"

        return before + text + after


def socket_parser(socket:str):
    symbol, interval = socket.split('@')

    symbol=symbol.upper()
    interval=interval.replace('kline_', '')

    return symbol, interval