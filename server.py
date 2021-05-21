import logging
import websockets
import json
import sys
import asyncio
from aiohttp import web
from functools import partial
from datetime import datetime, timezone, timedelta

from ocpp.routing import on
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result, call

import CentralSystem
import ChargePoint

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s.%(msecs)03d _%(levelname)s_ %(module)s - %(funcName)s: %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='log-server.log',
                    filemode='a')
# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s.%(msecs)03d _%(levelname)s_ %(module)s - %(funcName)s: %(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root logger
logging.getLogger('').addHandler(console)


VERSION = "0.0.1"
PORT1 = 9000    # EV CHARGER
PORT2 = 8000    # WEBSERVER
SERVERADDRESS = '0.0.0.0'
APIKEY = '6ICTtgQpX5FOmyEcRPbbhkDVsAqo5zRW'


"""""""""""""""""""""""""""""""""""""""""""""""""""
                Function for HTTP API
"""""""""""""""""""""""""""""""""""""""""""""""""""
async def unlock_connector(request):
    """ HTTP handler for unlock_connector of a charge points. """
    data = await request.json()
    csms = request.app["csms"]
    try:
        response = await csms.unlock_connector(data["chargerId"],data["connectorId"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to trigger_message  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)

async def trigger_message(request):
    """ HTTP handler for trigger message of a charge points. """
    data = await request.json()
    csms = request.app["csms"]
    try:
        response = await csms.trigger_message(data["chargerId"],data["connectorId"], data["requested_message"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to trigger_message  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)

async def change_availability(request):
    """ HTTP handler for change availability of all charge points. """
    data = await request.json()
    csms = request.app["csms"]
    try:
        response = await csms.change_availability(data["chargerId"],data["connectorId"], data["change_type"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to change_availability  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)

async def get_config(request):
    """ HTTP handler for changing configuration of all charge points. clsslslslcl"""
    data = await request.json()
    csms = request.app["csms"]
    try:
        response = await csms.get_configuration(data["chargerId"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to get_configuration  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def change_config(request):
    """ HTTP handler for changing configuration of all charge points. """
    data = await request.json()
    csms = request.app["csms"]
    try:
        response = await csms.change_configuration(data["chargerId"],data["key"], data["value"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to change_config start charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)



async def disconnect_charger(request):
    """ HTTP handler for disconnecting a charger. """
    data = await request.json()
    csms = request.app["csms"]
    try:
        csms.disconnect_charger(data["chargerId"])
    except ValueError as e:
        logging.error(f"Failed to disconnect charger: {e}")
        return web.Response(status=404)

    return web.Response()

async def remote_start(request):
    """ HTTP handler for remote starting a charger. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response = await csms.remotestart_charger(data["chargerId"],data["tag_id"],data["connectorId"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to remotely start charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)

async def remote_stop(request):
    """ HTTP handler for remote stoping a charger. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response = await csms.remotestop_charger(data["transaction_id"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to remotely stop charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)
    return web.Response(text=json.dumps(response_obj), status=200)

async def on_connect(websocket, path, csms):
    charge_point_id = path.strip("/")
    cp = ChargePoint.ChargePoint(charge_point_id, websocket)
    logging.info(f"The ChargePoint {cp.id} is registered on the CSMS.")

    # If this handler returns the connection will be destroyed. Therefore we need some
    # synchronization mechanism that blocks until CSMS wants to close the connection.
    # An `asyncio.Queue` is used for that.
    queue = csms.register_charger(cp)
    await queue.get()

async def create_websocket_server(csms: CentralSystem):
    handler = partial(on_connect, csms=csms)
    logging.info(f"The CentralSystem EV {SERVERADDRESS} is available at port {PORT1}.")
    return await websockets.serve(handler, 
                                 SERVERADDRESS, 
                                 PORT1, 
                                 subprotocols=["ocpp1.6"] , 
                                 ping_interval = None)

async def create_http_server(csms: CentralSystem):
    app = web.Application()
    app.add_routes([web.post("/changeconfig", change_config)])
    app.add_routes([web.post("/getconfig", get_config)])
    app.add_routes([web.post("/disconnect", disconnect_charger)])
    app.add_routes([web.post("/remotestart", remote_start)])
    app.add_routes([web.post("/remotestop", remote_stop)])
    app.add_routes([web.post("/changeavailability", change_availability)])
    app.add_routes([web.post("/tiggermsg", trigger_message)])
    app.add_routes([web.post("/unlockconnector", unlock_connector)])

    app["csms"] = csms
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, SERVERADDRESS, PORT2)
    logging.info(f"The HTTP API {SERVERADDRESS} is available at port {PORT2}.")
    return site

async def main():
    csms = CentralSystem.CentralSystem()
    logging.info("Central System processing...")
    websocket_server = await create_websocket_server(csms)
    logging.info("Create websocket_server done")
    http_server = await create_http_server(csms)
    logging.info("Create http_server done")
    await asyncio.wait([websocket_server.wait_closed(), http_server.start()])

if __name__ == "__main__":
    asyncio.run(main())