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