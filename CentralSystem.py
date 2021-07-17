import logging
import asyncio
from ocpp.routing import on,after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result, call
import ChargePoint

class CentralSystem:
    def __init__(self):
        self._chargers = {}

    def register_charger(self, cp: ChargePoint) -> asyncio.Queue:
        """ Register a new ChargePoint at the CSMS. The function returns a
        queue.  The CSMS will put a message on the queue if the CSMS wants to
        close the connection. 
        """
        queue = asyncio.Queue(maxsize=1)

        # Store a reference to the task so we can cancel it later if needed.
        task = asyncio.create_task(self.start_charger(cp, queue))
        self._chargers[cp] = task

        return queue

    async def start_charger(self, cp, queue):
        """ Start listening for message of charger. """
        try:
            await cp.start()
        except Exception as e:
            logging.warning(f"Charger {cp.id} disconnected. {e}")
        finally:
            # Make sure to remove reference to charger after it disconnected.
            del self._chargers[cp]

            # This will unblock the `on_connect()` handler and the connection
            # will be destroyed.
            await queue.put(True)

    def disconnect_charger(self, chargerId: str):
        for cp, task in self._chargers.items():
            if cp.id == chargerId:
                task.cancel()
                return 
        raise ValueError(f"Charger {chargerId} was not connected so I can not disconnect it.")

    async def remotestart_charger(self, chargerId: str , tag_id: str , connector_id:int):
        for cp, task in self._chargers.items():
            if cp.id == chargerId:
                logging.info(f"Charger {chargerId} is going to prepare charging!")
                response = await cp.remotestart_charger(chargerId,tag_id,connector_id)
                logging.info(f"Charger {chargerId} response : {response.status}")
                return response.status
        raise ValueError(f"Charger {chargerId} not connected!")
    
    async def remotestop_charger(self, transaction_id: int):
        for cp in self._chargers:
            logging.info(f"transaction_id {transaction_id} is going to stop charging!")
            response = await cp.remotestop_charger(transaction_id)
            logging.info(f"transaction_id {transaction_id} response : {response.status}")
            return response.status
        raise ValueError(f"transaction_id {transaction_id} not connected!")

    async def change_configuration(self, chargerId : str, key: str, value: str):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be change configuration")
                logging.info(f"The Charger {cp.id} will be change key   : {key}")
                logging.info(f"The Charger {cp.id} will be change value : {value}")
                response = await cp.change_configuration(key, value)
                logging.info(f"The Charger {cp.id} will be change configuration : {response.status} ")
                return response.status
                
    async def get_configuration(self, chargerId : str):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be get configuration")
                response = await cp.get_configuration()
                for data in response.configuration_key:
                    logging.info(f"The Charger {cp.id} got {data['key']} : {data['value']}")
                return response.configuration_key

    async def change_availability(self, chargerId : str , connector_id: int, change_type: str):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be change availability")
                logging.info(f"The Charger {cp.id} will be change availability with connector_id   : {connector_id}")
                logging.info(f"The Charger {cp.id} will be change availability with change_type : {change_type}")
                response = await cp.change_availability(connector_id, change_type)
                logging.info(f"The Charger {cp.id} will be change availability {change_type} was {response.status} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")

    async def trigger_message(self, chargerId : str , connector_id: int, requested_message: str):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be trigger message")
                logging.info(f"The Charger {cp.id} will be trigger message with connector_id      : {connector_id}")
                logging.info(f"The Charger {cp.id} will be trigger message with requested_message : {requested_message}")
                response = await cp.trigger_message(requested_message, connector_id)
                logging.info(f"The Charger {cp.id} got trigger message {requested_message} was {response.status} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")

    async def unlock_connector(self, chargerId : str , connector_id: int):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be unlock connector")
                logging.info(f"The Charger {cp.id} will be unlock connector with connector_id      : {connector_id}")
                response = await cp.unlock_connector(connector_id)
                logging.info(f"The Charger {cp.id} got unlock connector with {connector_id} was {response.status} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")
        
    async def reset(self, chargerId : str,reset_type: str):
        
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be reset ")
                logging.info(f"The Charger {cp.id} will be reset message with chargerId      : {chargerId}")
                response = await cp.reset(reset_type)
                logging.info(f"The Charger {cp.id} got be reset message {reset_type} was {response.status} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")

    async def reservenow(self, chargerId : str,connectorId: int,expiryDate : str,idTag:str,reservationId:int):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be reservenow ")
                logging.info(f"The Charger {cp.id} will be reservenow message with chargerId      : {chargerId}")
                logging.info(f"The Charger {cp.id} will be reservenow message with connectorId    : {connectorId}")
                logging.info(f"The Charger {cp.id} will be reservenow message with expiryDate     : {expiryDate}")
                logging.info(f"The Charger {cp.id} will be reservenow message with idTag          : {idTag}")
                logging.info(f"The Charger {cp.id} will be reservenow message with reservationId  : {reservationId}")
                response = await cp.reservenow(connectorId,expiryDate,idTag,reservationId)
                logging.info(f"The Charger {cp.id} got be reservenow message {chargerId} was {response.status} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")
        
    async def cancelreservenow(self, chargerId : str,reservationId:int):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be cancel reservenow ")
                logging.info(f"The Charger {cp.id} will be cancel reservenow message with chargerId      : {chargerId}")
                logging.info(f"The Charger {cp.id} will be cancel reservenow message with reservationId  : {reservationId}")
                response = await cp.cancelreservenow(reservationId)
                logging.info(f"The Charger {cp.id} got be cancel reservenow message {chargerId} was {response.status} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")
    
    async def setdatatransfer(self, chargerId : str,vendorId:str, messageId : str,data:str):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be setdatatransfer ")
                logging.info(f"The Charger {cp.id} will be setdatatransfer message with chargerId  : {chargerId}")
                logging.info(f"The Charger {cp.id} will be setdatatransfer message with vendorId   : {vendorId}")
                logging.info(f"The Charger {cp.id} will be setdatatransfer message with messageId  : {messageId}")
                logging.info(f"The Charger {cp.id} will be setdatatransfer message with data       : {data}")
                response = await cp.setdatatransfer(vendorId,messageId,data)
                logging.info(f"The Charger {cp.id} got be setdatatransfer message {chargerId} was {response.status}  ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")
        
    async def getdatatransfer(self, chargerId : str,vendorId:str, messageId : str):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be getdatatransfer ")
                logging.info(f"The Charger {cp.id} will be getdatatransfer message with chargerId  : {chargerId}")
                logging.info(f"The Charger {cp.id} will be getdatatransfer message with vendorId   : {vendorId}")
                logging.info(f"The Charger {cp.id} will be getdatatransfer message with messageId  : {messageId}")
                response = await cp.getdatatransfer(vendorId,messageId)
                logging.info(f"The Charger {cp.id} got be getdatatransfer message {chargerId} was {response.status} with {response.data} ")
                return response.status,response.data
        raise ValueError(f"The Charger {chargerId} not connected!")
    
    async def updatefirmware(self, chargerId : str,location:str, retries : int,retrieveDate:str,retryInterval:int):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be updatefirmware ")
                logging.info(f"The Charger {cp.id} will be updatefirmware message with chargerId    : {chargerId}")
                logging.info(f"The Charger {cp.id} will be updatefirmware message with location     : {location}")
                logging.info(f"The Charger {cp.id} will be updatefirmware message with retries      : {retries}")
                logging.info(f"The Charger {cp.id} will be updatefirmware message with retrieveDate : {retrieveDate}")
                logging.info(f"The Charger {cp.id} will be updatefirmware message with retryInterval: {retryInterval}")
                response = await cp.updatefirmware(location,retries,retrieveDate,retryInterval)
                logging.info(f"The Charger {cp.id} got be updatefirmware message {chargerId} was {response} ")
                return response
        raise ValueError(f"The Charger {chargerId} not connected!")
        
    async def getcompositeschedule(self, chargerId : str,connectorId:int, duration : int,chargingRateUnit:str =None):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be getcompositeschedule ")
                logging.info(f"The Charger {cp.id} will be getcompositeschedule message with chargerId       : {chargerId}")
                logging.info(f"The Charger {cp.id} will be getcompositeschedule message with connectorId     : {connectorId}")
                logging.info(f"The Charger {cp.id} will be getcompositeschedule message with duration        : {duration}")
                logging.info(f"The Charger {cp.id} will be getcompositeschedule message with chargingRateUnit: {chargingRateUnit}")
                response = await cp.getcompositeschedule(connectorId,duration,chargingRateUnit)
                logging.info(f"The Charger {cp.id} got be getcompositeschedule  message {chargerId} was {response} ")
                return response.status,response.connector_id,response.schedule_start,response.charging_schedule
        raise ValueError(f"The Charger {chargerId} not connected!")
    
    async def setchargingprofile(self, chargerId : str,connectorId:int, csChargingProfiles : dict):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be setchargingprofile")
                logging.info(f"The Charger {cp.id} will be setchargingprofile message with chargerId          : {chargerId}")
                logging.info(f"The Charger {cp.id} will be setchargingprofile message with connectorId        : {connectorId}")
                logging.info(f"The Charger {cp.id} will be setchargingprofile message with csChargingProfiles : {csChargingProfiles}")
                response = await cp.setchargingprofile(connectorId,csChargingProfiles)
                logging.info(f"The Charger {cp.id} got be setchargingprofile  message {chargerId} was {response} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")
    
    async def clearchargingprofile(self, chargerId : str,data_id:int, connectorId : int,chargingProfilePurpose : str,stackLevel:int):
        for cp in self._chargers:
            if cp.id == chargerId:
                logging.info(f"The Charger {cp.id} will be clearchargingprofile")
                logging.info(f"The Charger {cp.id} will be clearchargingprofile message with chargerId               : {chargerId}")
                logging.info(f"The Charger {cp.id} will be clearchargingprofile message with id                      : {data_id}")
                logging.info(f"The Charger {cp.id} will be clearchargingprofile message with connectorId             : {connectorId}")
                logging.info(f"The Charger {cp.id} will be clearchargingprofile message with chargingProfilePurpose  : {chargingProfilePurpose}")
                logging.info(f"The Charger {cp.id} will be clearchargingprofile message with stackLevel              : {stackLevel}")
                response = await cp.clearchargingprofile(data_id,connectorId,chargingProfilePurpose,stackLevel)
                logging.info(f"The Charger {cp.id} got be clearchargingprofile  message {chargerId} was {response} ")
                return response.status
        raise ValueError(f"The Charger {chargerId} not connected!")
