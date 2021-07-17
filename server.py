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
PORT_EV = 9001    # EV CHARGER
PORT_API = 8001    # WEBSERVER
SERVERADDRESS = '0.0.0.0'
APIKEY = '6ICTtgQpX5FOmyEcRPbbhkDVsAqo5zRW'

async def clearchargingprofile(request):
    """ HTTP handler for clear charging profile a charge points. """
    data = await request.json()
    print(data)
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response_status = await csms.clearchargingprofile(data["chargerId"],data["id"],data["connectorId"],data["chargingProfilePurpose"],data["stackLevel"])
        response_obj = { 'status' : response_status}
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def setchargingprofile(request):
    """ HTTP handler for Set charging profile a charge points. """
    data = await request.json()
    print(data)
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response_status = await csms.setchargingprofile(data["chargerId"],data["connectorId"],data["csChargingProfiles"])
        response_obj = { 'status' : response_status}
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def getcompositeschedule(request):
    """ HTTP handler for get composite schedule a charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response_status,response_connector_id,response_schedule_start,response_charging_schedule = await csms.getcompositeschedule(data["chargerId"],data["connectorId"],data["duration"],data["chargingRateUnit"])
        response_obj = { 'status' : response_status,'connector_id' : response_connector_id,'schedule_start' : response_schedule_start,'charging_schedule' : response_charging_schedule}
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def updatefirmware(request):
    """ HTTP handler for update fw a charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response_status = await csms.updatefirmware(data["chargerId"],data["location"],data["retries"],data["retrieveDate"],data["retryInterval"])
        response_obj = { 'status' : 'Accept'}
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def getdatatransfer(request):
    """ HTTP handler for update qr code a charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response_status,response_data = await csms.getdatatransfer(data["chargerId"],data["vendorId"],data["messageId"])
        response_obj = { 'status' : response_status,'data' : response_data }
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def setdatatransfer(request):
    """ HTTP handler for update qr code a charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response = await csms.setdatatransfer(data["chargerId"],data["vendorId"],data["messageId"],data["data"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def cancelreservenow(request):
    """ HTTP handler for reset all charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response = await csms.cancelreservenow(data["chargerId"],data["reservationId"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def reservenow(request):
    """ HTTP handler for reset all charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response = await csms.reservenow(data["chargerId"],data["connectorId"],data["expiryDate"],data["idTag"],data["reservationId"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)
    
async def reset(request):
    """ HTTP handler for reset all charge points. """
    data = await request.json()
    csms = request.app["csms"]
    if data["apikey"]!=APIKEY:
        logging.error("API key is not valid")
        response_obj = { 'status' : 'failed', 'reason': f'API key is not valid {data["apikey"]}' }
        return web.Response(text=json.dumps(response_obj), status=404)
    try:
        response = await csms.reset(data["chargerId"],data["type"])
        response_obj = { 'status' : response }
    except ValueError as e:
        logging.error(f"Failed to reset  charger: {e}")
        response_obj = { 'status' : 'failed', 'reason': str(e) }
        return web.Response(text=json.dumps(response_obj), status=404)

    return web.Response(text=json.dumps(response_obj), status=200)

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
    logging.info(f"The CentralSystem EV {SERVERADDRESS} is available at port {PORT_EV}.")
    return await websockets.serve(handler, 
                                 SERVERADDRESS, 
                                 PORT_EV, 
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
    app.add_routes([web.post("/reset", reset)])
    app.add_routes([web.post("/reservenow", reservenow)])
    app.add_routes([web.post("/cancelreservenow", cancelreservenow)])
    app.add_routes([web.post("/setdatatransfer", setdatatransfer)])
    app.add_routes([web.post("/getdatatransfer", getdatatransfer)])
    app.add_routes([web.post("/updatefirmware", updatefirmware)])
    app.add_routes([web.post("/getcompositeschedule", getcompositeschedule)])
    app.add_routes([web.post("/setchargingprofile", setchargingprofile)])
    app.add_routes([web.post("/clearchargingprofile",clearchargingprofile)])

    app["csms"] = csms
    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, SERVERADDRESS, PORT_API)
    logging.info(f"The HTTP API {SERVERADDRESS} is available at port {PORT_API}.")
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
    try:
        # asyncio.run() is used when running this example with Python 3.7 and
        # higher.
        asyncio.run(main())
    except AttributeError:
        # For Python 3.6 a bit more code is required to run the main() task on
        # an event loop.
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
        loop.close()
