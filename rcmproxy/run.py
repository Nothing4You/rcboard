import asyncio
import logging

import aiohttp

from .log import logging_config

from .api_server import ApiServer


UPSTREAM_IP = "127.0.0.1"

ENABLE_DUMMY = True
ENABLE_POLL = False
ENABLE_WS = False


PROXY_LISTEN_IP = "0.0.0.0"
PROXY_LISTEN_PORT = 5080


logging_config()
logger = logging.getLogger("rcmproxy.run")


async def ws_backend(cb, session: aiohttp.ClientSession = None):
    ws_logger = logging.getLogger("rcmproxy.run.ws_backend")

    if session is None:
        session = aiohttp.ClientSession()

    while True:
        try:
            async with session.ws_connect(f"http://{UPSTREAM_IP}:8787/") as ws:
                async for msg in ws:
                    msg: aiohttp.WSMessage

                    if msg.type == aiohttp.WSMsgType.TEXT:
                        ws_logger.debug("Received WSMessage of type WSMsgType.TEXT")
                        ws_logger.debug(msg.data)
                        await cb(msg.data, type_="StreamingData")

                    else:
                        ws_logger.warning(f"Unexpexted WSMsgType: {msg.type}")
                        ws_logger.debug(msg)

                    # ws_logger.debug(msg)
                    # ws_logger.debug(msg.type)
                    # ws_logger.debug(msg.data)

                    # if msg.type == aiohttp.WSMsgType.TEXT:
                    #     if msg.data == 'close cmd':
                    #         await ws.close()
                    #         break
                    #     else:
                    #         await ws.send_str(msg.data + '/answer')
                    # elif msg.type == aiohttp.WSMsgType.ERROR:
                    #     break
        except aiohttp.ClientError as e:
            ws_logger.debug(e, exc_info=True)
            ws_logger.warning(e)
            await asyncio.sleep(0.1)


async def poll_task(type_: str, cb, session: aiohttp.ClientSession):
    pt_logger = logging.getLogger("rcmproxy.run.poll_task")

    try:
        async with session.get(f"http://{UPSTREAM_IP}/1/{type_}") as resp:
            try:
                resp.raise_for_status()

                text = await resp.text()
                # pt_logger.debug(text)
                pt_logger.debug(f"Retrieving http://{UPSTREAM_IP}/1/{type_}")

                if len(text) == 0:
                    return

                await cb(text, type_=type_)
                # task.add_done_callback(lambda t: tasks.remove(t))

            except aiohttp.ClientResponseError as e:
                pt_logger.warning("Unexpected http status code")
                pt_logger.debug(e, exc_info=True)
                pt_logger.warning(e)
    except aiohttp.ClientConnectorError:
        pt_logger.warning(f"Unable to connect to upstream: http://{UPSTREAM_IP}/1/{type_}")


async def poll_backend(cb, session: aiohttp.ClientSession, interval: int = None):
    if interval is None:
        interval = 0.2

    tasks = []

    # types = {"Info", "EventList", "StreamingData"}
    types = {"StreamingData"}

    while True:
        for type_ in types:
            tasks.append(poll_task(type_, cb, session))

        tasks.append(asyncio.sleep(interval))

        await asyncio.gather(*tasks)
        tasks.clear()


async def dummy_backend(cb):
    from .dummy_backend import data

    while True:
        for line in data:
            await cb(line, type_="StreamingData")
            await asyncio.sleep(0.2)

    import random
    while True:
        data = [
            '{"EVENT":{"VERSION":"1.0","KEY":"B18D6AD13C82725D5401","TIMESTAMP":"9058663","CONFIG":{"MODE":"BestTime","NROFBESTLAPS":3},"METADATA":{"NAME":"Euro Touring Series R1 Vienna \/ AT","SECTION":"Xray Pro Stock","GROUP":"Xray Pro Stock :: Timed practice :: Group 20 - Heat 2","RACETIME":"00:04:00","CURRENTTIME":"00:01:01","REMAININGTIME":"00:02:59","COUNTDOWN":"00:00:00","DIVERGENCE":"00:00:00"},"DATA":[{"COLOR":7,"INDEX":1,"VEHICLE":1,"PILOTNUMBER":0,"TRANSPONDER":"7455555","PILOT":"MÄCHLER Max","CLUB":"Die Kurvekuggler e.V.","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":3,"LAPTIME":"14.583","ABSOLUTTIME":"00:55.514","BESTTIME":"14.465","BESTTIMEN":"43.688","MEDIUMTIME":"18.504","FORECAST":"16 04:04.820","PROGRESS":36,"DELAYTIMEFIRST":"0.000","DELAYTIMEPREVIOUS":"0.000","STANDARDDEVIATION":"0.089","CARID":0,"VOLTAGE":"n\/a","TEMPERATUR":"n\/a","SPEED":"41.23"},{"COLOR":7,"INDEX":2,"VEHICLE":10,"PILOTNUMBER":0,"TRANSPONDER":"2123309","PILOT":"RATHEISKY Jan","CLUB":"Team XRAY","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.685","ABSOLUTTIME":"00:58.416","BESTTIME":"14.521","BESTTIMEN":"43.731","MEDIUMTIME":"14.604","FORECAST":"17 04:08.268","PROGRESS":15,"DELAYTIMEFIRST":"+0.056","DELAYTIMEPREVIOUS":"+0.056","STANDARDDEVIATION":"0.074","CARID":0,"VOLTAGE":"5.8 V","TEMPERATUR":"25 °C","SPEED":"40.94"},{"COLOR":7,"INDEX":3,"VEHICLE":9,"PILOTNUMBER":0,"TRANSPONDER":"2598314","PILOT":"BENSON Tim","CLUB":"MAC Hamburg e.V.","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":3,"LAPTIME":"14.713","ABSOLUTTIME":"00:53.359","BESTTIME":"14.525","BESTTIMEN":"43.776","MEDIUMTIME":"17.786","FORECAST":"16 04:03.055","PROGRESS":50,"DELAYTIMEFIRST":"+0.060","DELAYTIMEPREVIOUS":"+0.004","STANDARDDEVIATION":"0.104","CARID":0,"VOLTAGE":"5.9 V","TEMPERATUR":"25 °C","SPEED":"40.86"},{"COLOR":7,"INDEX":4,"VEHICLE":6,"PILOTNUMBER":0,"TRANSPONDER":"7674494","PILOT":"BULTYNCK Olivier","CLUB":"Awesomatix \/ Roche \/ LRP","COUNTRY":"BE","LAPINFO":"","TREND":0,"LAPS":3,"LAPTIME":"14.714","ABSOLUTTIME":"00:49.894","BESTTIME":"14.714","BESTTIMEN":"44.250","MEDIUMTIME":"16.631","FORECAST":"16 04:01.644","PROGRESS":73,"DELAYTIMEFIRST":"+0.249","DELAYTIMEPREVIOUS":"+0.189","STANDARDDEVIATION":"0.033","CARID":0,"VOLTAGE":"5.3 V","TEMPERATUR":"24 °C","SPEED":"40.86"},{"COLOR":2,"INDEX":5,"VEHICLE":2,"PILOTNUMBER":0,"TRANSPONDER":"2256295","PILOT":"KUNKLER Alex","CLUB":"MRC LONGWY","COUNTRY":"FR","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.694","ABSOLUTTIME":"01:00.542","BESTTIME":"14.694","BESTTIMEN":"44.252","MEDIUMTIME":"15.135","FORECAST":"17 04:12.656","PROGRESS":1,"DELAYTIMEFIRST":"+0.229","DELAYTIMEPREVIOUS":"+2:47.276","STANDARDDEVIATION":"0.072","CARID":0,"VOLTAGE":"5.9 V","TEMPERATUR":"25 °C","SPEED":"40.91"},{"COLOR":7,"INDEX":6,"VEHICLE":11,"PILOTNUMBER":0,"TRANSPONDER":"3457797","PILOT":"WEGMANN Markus","CLUB":"RCSF-Singen e.V.","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":3,"LAPTIME":"14.980","ABSOLUTTIME":"00:54.728","BESTTIME":"14.726","BESTTIMEN":"44.558","MEDIUMTIME":"18.242","FORECAST":"16 04:07.804","PROGRESS":40,"DELAYTIMEFIRST":"+0.261","DELAYTIMEPREVIOUS":"+0.032","STANDARDDEVIATION":"0.127","CARID":0,"VOLTAGE":"n\/a","TEMPERATUR":"n\/a","SPEED":"40.13"},{"COLOR":7,"INDEX":7,"VEHICLE":8,"PILOTNUMBER":0,"TRANSPONDER":"7599084","PILOT":"ARNOLD Léo","CLUB":"","COUNTRY":"MC","LAPINFO":"","TREND":0,"LAPS":3,"LAPTIME":"15.016","ABSOLUTTIME":"00:57.841","BESTTIME":"14.749","BESTTIMEN":"44.706","MEDIUMTIME":"19.280","FORECAST":"16 04:11.567","PROGRESS":19,"DELAYTIMEFIRST":"+0.284","DELAYTIMEPREVIOUS":"+0.023","STANDARDDEVIATION":"0.137","CARID":0,"VOLTAGE":"5.5 V","TEMPERATUR":"24 °C","SPEED":"40.04"},{"COLOR":7,"INDEX":8,"VEHICLE":7,"PILOTNUMBER":0,"TRANSPONDER":"6452076","PILOT":"HOPPE Lars","CLUB":"AMC Hildesheim","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":3,"LAPTIME":"14.927","ABSOLUTTIME":"00:57.341","BESTTIME":"14.827","BESTTIMEN":"44.935","MEDIUMTIME":"19.113","FORECAST":"16 04:12.055","PROGRESS":22,"DELAYTIMEFIRST":"+0.362","DELAYTIMEPREVIOUS":"+0.078","STANDARDDEVIATION":"0.182","CARID":0,"VOLTAGE":"5.9 V","TEMPERATUR":"25 °C","SPEED":"40.28"},{"COLOR":7,"INDEX":9,"VEHICLE":5,"PILOTNUMBER":0,"TRANSPONDER":"3674810","PILOT":"MIKKELSEN Frederik Broløs","CLUB":"Team Tonisport","COUNTRY":"DK","LAPINFO":"","TREND":-1,"LAPS":3,"LAPTIME":"15.387","ABSOLUTTIME":"00:55.816","BESTTIME":"14.837","BESTTIMEN":"45.079","MEDIUMTIME":"18.605","FORECAST":"16 04:11.154","PROGRESS":32,"DELAYTIMEFIRST":"+0.372","DELAYTIMEPREVIOUS":"+0.010","STANDARDDEVIATION":"0.312","CARID":0,"VOLTAGE":"7.5 V","TEMPERATUR":"24 °C","SPEED":"39.07"},{"COLOR":7,"INDEX":10,"VEHICLE":4,"PILOTNUMBER":0,"TRANSPONDER":"5286218","PILOT":"HOFER Martin","CLUB":"Team Yokomo","COUNTRY":"DE","LAPINFO":"","TREND":1,"LAPS":3,"LAPTIME":"14.850","ABSOLUTTIME":"00:59.089","BESTTIME":"14.850","BESTTIMEN":"45.120","MEDIUMTIME":"19.696","FORECAST":"16 04:14.609","PROGRESS":10,"DELAYTIMEFIRST":"+0.385","DELAYTIMEPREVIOUS":"+0.013","STANDARDDEVIATION":"0.203","CARID":0,"VOLTAGE":"n\/a","TEMPERATUR":"n\/a","SPEED":"40.48"},{"COLOR":7,"INDEX":11,"VEHICLE":3,"PILOTNUMBER":0,"TRANSPONDER":"4195054","PILOT":"OLSEN Steven M.","CLUB":"Team Awesomatix","COUNTRY":"DK","LAPINFO":"","TREND":1,"LAPS":3,"LAPTIME":"15.258","ABSOLUTTIME":"00:47.647","BESTTIME":"15.258","BESTTIMEN":"47.085","MEDIUMTIME":"15.882","FORECAST":"16 04:11.682","PROGRESS":83,"DELAYTIMEFIRST":"+0.793","DELAYTIMEPREVIOUS":"+0.408","STANDARDDEVIATION":"0.591","CARID":0,"VOLTAGE":"6.0 V","TEMPERATUR":"23 °C","SPEED":"39.40"}]}}',
            '{"EVENT":{"VERSION":"1.0","KEY":"B18D6AD13C82725D5401","TIMESTAMP":"9076894","CONFIG":{"MODE":"BestTime","NROFBESTLAPS":3},"METADATA":{"NAME":"Euro Touring Series R1 Vienna \/ AT","SECTION":"Xray Pro Stock","GROUP":"Xray Pro Stock :: Timed practice :: Group 20 - Heat 2","RACETIME":"00:04:00","CURRENTTIME":"00:01:19","REMAININGTIME":"00:02:41","COUNTDOWN":"00:00:00","DIVERGENCE":"00:00:00"},"DATA":[{"COLOR":7,"INDEX":1,"VEHICLE":1,"PILOTNUMBER":0,"TRANSPONDER":"7455555","PILOT":"MÄCHLER Max","CLUB":"Die Kurvekuggler e.V.","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.405","ABSOLUTTIME":"01:09.919","BESTTIME":"14.405","BESTTIMEN":"43.628","MEDIUMTIME":"17.479","FORECAST":"16 04:04.195","PROGRESS":61,"DELAYTIMEFIRST":"0.000","DELAYTIMEPREVIOUS":"0.000","STANDARDDEVIATION":"0.107","CARID":0,"VOLTAGE":"n\/a","TEMPERATUR":"n\/a","SPEED":"41.74"},{"COLOR":7,"INDEX":2,"VEHICLE":10,"PILOTNUMBER":0,"TRANSPONDER":"2123309","PILOT":"RATHEISKY Jan","CLUB":"Team XRAY","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.628","ABSOLUTTIME":"01:13.044","BESTTIME":"14.521","BESTTIMEN":"43.731","MEDIUMTIME":"14.608","FORECAST":"17 04:08.472","PROGRESS":38,"DELAYTIMEFIRST":"+0.116","DELAYTIMEPREVIOUS":"+0.116","STANDARDDEVIATION":"0.065","CARID":0,"VOLTAGE":"5.8 V","TEMPERATUR":"25 °C","SPEED":"41.10"},{"COLOR":7,"INDEX":3,"VEHICLE":9,"PILOTNUMBER":0,"TRANSPONDER":"2598314","PILOT":"BENSON Tim","CLUB":"MAC Hamburg e.V.","COUNTRY":"DE","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.643","ABSOLUTTIME":"01:08.002","BESTTIME":"14.525","BESTTIMEN":"43.776","MEDIUMTIME":"17.000","FORECAST":"16 04:03.250","PROGRESS":74,"DELAYTIMEFIRST":"+0.120","DELAYTIMEPREVIOUS":"+0.004","STANDARDDEVIATION":"0.089","CARID":0,"VOLTAGE":"5.9 V","TEMPERATUR":"25 °C","SPEED":"41.06"},{"COLOR":7,"INDEX":4,"VEHICLE":2,"PILOTNUMBER":0,"TRANSPONDER":"2256295","PILOT":"KUNKLER Alex","CLUB":"MRC LONGWY","COUNTRY":"FR","LAPINFO":"","TREND":0,"LAPS":5,"LAPTIME":"14.659","ABSOLUTTIME":"01:15.201","BESTTIME":"14.659","BESTTIMEN":"44.101","MEDIUMTIME":"15.040","FORECAST":"17 04:11.925","PROGRESS":24,"DELAYTIMEFIRST":"+0.254","DELAYTIMEPREVIOUS":"+0.134","STANDARDDEVIATION":"0.082","CARID":0,"VOLTAGE":"5.9 V","TEMPERATUR":"25 °C","SPEED":"41.01"},{"COLOR":7,"INDEX":5,"VEHICLE":11,"PILOTNUMBER":0,"TRANSPONDER":"3457797","PILOT":"WEGMANN Markus","CLUB":"RCSF-Singen e.V.","COUNTRY":"DE","LAPINFO":"","TREND":1,"LAPS":4,"LAPTIME":"14.503","ABSOLUTTIME":"01:09.231","BESTTIME":"14.503","BESTTIMEN":"44.209","MEDIUMTIME":"17.307","FORECAST":"16 04:06.411","PROGRESS":64,"DELAYTIMEFIRST":"+0.098","DELAYTIMEPREVIOUS":"+2:47.140","STANDARDDEVIATION":"0.203","CARID":0,"VOLTAGE":"n\/a","TEMPERATUR":"n\/a","SPEED":"41.45"},{"COLOR":1,"INDEX":6,"VEHICLE":6,"PILOTNUMBER":0,"TRANSPONDER":"7674494","PILOT":"BULTYNCK Olivier","CLUB":"Awesomatix \/ Roche \/ LRP","COUNTRY":"BE","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.789","ABSOLUTTIME":"01:04.683","BESTTIME":"14.714","BESTTIMEN":"44.250","MEDIUMTIME":"16.170","FORECAST":"16 04:01.791","PROGRESS":95,"DELAYTIMEFIRST":"+0.309","DELAYTIMEPREVIOUS":"+0.211","STANDARDDEVIATION":"0.033","CARID":0,"VOLTAGE":"5.3 V","TEMPERATUR":"24 °C","SPEED":"40.65"},{"COLOR":7,"INDEX":7,"VEHICLE":8,"PILOTNUMBER":0,"TRANSPONDER":"7599084","PILOT":"ARNOLD Léo","CLUB":"","COUNTRY":"MC","LAPINFO":"","TREND":1,"LAPS":4,"LAPTIME":"14.656","ABSOLUTTIME":"01:12.497","BESTTIME":"14.656","BESTTIMEN":"44.421","MEDIUMTIME":"18.124","FORECAST":"16 04:10.577","PROGRESS":42,"DELAYTIMEFIRST":"+0.251","DELAYTIMEPREVIOUS":"+2:47.238","STANDARDDEVIATION":"0.166","CARID":0,"VOLTAGE":"5.5 V","TEMPERATUR":"24 °C","SPEED":"41.02"},{"COLOR":7,"INDEX":8,"VEHICLE":4,"PILOTNUMBER":0,"TRANSPONDER":"5286218","PILOT":"HOFER Martin","CLUB":"Team Yokomo","COUNTRY":"DE","LAPINFO":"","TREND":1,"LAPS":4,"LAPTIME":"14.684","ABSOLUTTIME":"01:13.773","BESTTIME":"14.684","BESTTIMEN":"44.788","MEDIUMTIME":"18.443","FORECAST":"16 04:13.185","PROGRESS":33,"DELAYTIMEFIRST":"+0.279","DELAYTIMEPREVIOUS":"+0.028","STANDARDDEVIATION":"0.243","CARID":0,"VOLTAGE":"n\/a","TEMPERATUR":"n\/a","SPEED":"40.94"},{"COLOR":7,"INDEX":9,"VEHICLE":7,"PILOTNUMBER":0,"TRANSPONDER":"6452076","PILOT":"HOPPE Lars","CLUB":"AMC Hildesheim","COUNTRY":"DE","LAPINFO":"","TREND":-1,"LAPS":4,"LAPTIME":"15.543","ABSOLUTTIME":"01:12.884","BESTTIME":"14.827","BESTTIMEN":"44.935","MEDIUMTIME":"18.221","FORECAST":"16 04:14.312","PROGRESS":38,"DELAYTIMEFIRST":"+0.422","DELAYTIMEPREVIOUS":"+0.143","STANDARDDEVIATION":"0.319","CARID":0,"VOLTAGE":"5.9 V","TEMPERATUR":"25 °C","SPEED":"38.68"},{"COLOR":7,"INDEX":10,"VEHICLE":5,"PILOTNUMBER":0,"TRANSPONDER":"3674810","PILOT":"MIKKELSEN Frederik Broløs","CLUB":"Team Tonisport","COUNTRY":"DK","LAPINFO":"","TREND":0,"LAPS":4,"LAPTIME":"14.934","ABSOLUTTIME":"01:10.750","BESTTIME":"14.837","BESTTIMEN":"45.079","MEDIUMTIME":"17.687","FORECAST":"16 04:10.786","PROGRESS":53,"DELAYTIMEFIRST":"+0.432","DELAYTIMEPREVIOUS":"+0.010","STANDARDDEVIATION":"0.259","CARID":0,"VOLTAGE":"7.5 V","TEMPERATUR":"24 °C","SPEED":"40.26"},{"COLOR":7,"INDEX":11,"VEHICLE":3,"PILOTNUMBER":0,"TRANSPONDER":"4195054","PILOT":"OLSEN Steven M.","CLUB":"Team Awesomatix","COUNTRY":"DK","LAPINFO":"","TREND":0,"LAPS":5,"LAPTIME":"15.267","ABSOLUTTIME":"01:17.760","BESTTIME":"14.846","BESTTIMEN":"45.371","MEDIUMTIME":"15.552","FORECAST":"16 04:05.037","PROGRESS":6,"DELAYTIMEFIRST":"+0.441","DELAYTIMEPREVIOUS":"+0.009","STANDARDDEVIATION":"0.565","CARID":0,"VOLTAGE":"6.0 V","TEMPERATUR":"24 °C","SPEED":"39.38"}]}}',
        ]

        await cb(random.choice(data), type_="StreamingData")
        await asyncio.sleep(3)


async def main():
    f = []

    timeout = aiohttp.ClientTimeout(sock_connect=5, total=30)

    cs = aiohttp.ClientSession(timeout=timeout)

    api_server = ApiServer(host=PROXY_LISTEN_IP, port=PROXY_LISTEN_PORT)
    await api_server.start()

    async def cb(data: str, type_: str = None):
        await api_server.distribute(data, type_)

    if ENABLE_WS:
        f.append(ws_backend(cb, cs))

    if ENABLE_POLL:
        f.append(poll_backend(cb, cs))

    if ENABLE_DUMMY:
        f.append(dummy_backend(cb))

    await asyncio.gather(*f)
