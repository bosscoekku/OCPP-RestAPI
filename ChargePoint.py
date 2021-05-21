import logging
from datetime import datetime, timezone, timedelta
from ocpp.routing import on,after
from ocpp.v16 import ChargePoint as cp
from ocpp.v16.enums import Action, RegistrationStatus
from ocpp.v16 import call_result, call

class ChargePoint(cp):
    @on(Action.BootNotification)
    def get_boot_notification(self, charge_point_vendor: str, charge_point_model: str, **kwargs):
        logging.info(f"receive charge_point_vendor : {charge_point_vendor}")
        logging.info(f"receive charge_point_model  : {charge_point_model}")
        return call_result.BootNotificationPayload(
            current_time = datetime.now(tz=timezone(timedelta(hours = 7))).strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            interval = 10,
            status = RegistrationStatus.accepted
        )
        
    @on(Action.Heartbeat)
    def get_Heartbeat(self):
        return call_result.HeartbeatPayload(
            current_time = datetime.now(tz=timezone(timedelta(hours = 7))).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        )
        
    @on(Action.StatusNotification)
    def get_StatusNotification(self,connector_id: int, error_code: str,status: str):
        logging.info(f"receive connector_id  : {connector_id}")
        logging.info(f"receive error_code    : {error_code}")
        logging.info(f"receive status        : {status}")
        return call_result.StatusNotificationPayload()
        
    @on(Action.MeterValues)
    def get_MeterValues(self,transaction_id: int,connector_id: int,meter_value : list):
        logging.info(f"receive transaction_id  : {transaction_id}")
        logging.info(f"receive connector_id    : {connector_id}")
        logging.info(f"receive meter_value     : {meter_value}")
        return call_result.MeterValuesPayload()

    @on(Action.StartTransaction)
    def get_StartTransaction(self, connector_id: int, id_tag: str,meter_start: int, timestamp : str):
        logging.info(f"receive connector_id  : {connector_id}")
        logging.info(f"receive id_tag        : {id_tag}")
        logging.info(f"receive meter_start   : {meter_start}")
        logging.info(f"receive timestamp     : {timestamp}")
        return call_result.StartTransactionPayload(
        id_tag_info = {
            "status" : "Accepted"
            },
        transaction_id = 1008611006      
        )

    @on(Action.StopTransaction)
    def get_StopTransaction(self,meter_stop: int, timestamp : str ,transaction_id: int, reason : str):
        logging.info(f"receive transaction_id  : {transaction_id}")
        logging.info(f"receive reason          : {reason}")
        logging.info(f"receive meter_stop      : {meter_stop}")
        logging.info(f"receive timestamp       : {timestamp}")
        return call_result.StopTransactionPayload(
        id_tag_info = {
            "status" : "Accepted"
            }
        )
    
    @on(Action.Authorize)
    async def get_Authorize(self,id_tag : str ):
        logging.info(f"receive id_tag  : {id_tag}")
        return call_result.AuthorizePayload(
        id_tag_info = {
            "status" : "Accepted"
            }
        )
    
    #@on(Action.GetConfiguration)
    #async def get_Configuration(self,**kwargs):
    #    logging.info(f"receive kwargs : {kwargs}")
    #    return call_result.GetConfigurationPayload()

    async def reset_charger(self):
        request = call.ResetPayload(
            type="Soft"
        )
        response = await self.call(request)
        logging.info(response)
        return response
    
    async def remotestart_charger(self, chargerId: str , tag_id: str , connector_id:int):
        request = call.RemoteStartTransactionPayload(
            id_tag = tag_id,
            connector_id = connector_id
        )
        response = await self.call(request)
        return response
    
    async def remotestop_charger(self, transaction_id: int):
        request = call.RemoteStopTransactionPayload(
            transaction_id = transaction_id
        )
        response = await self.call(request)
        return response

    async def change_configuration(self, key: str, value: str):
        request = call.ChangeConfigurationPayload(
                                                    key=key, 
                                                    value=value
                                                )
        response = await self.call(request)
        return response

    async def get_configuration(self):
        request = call.GetConfigurationPayload()
        response = await self.call(request)
        return response
        
    """
    Requested availability change in ChangeAvailability.req.

    inoperative = "Inoperative"
    operative = "Operative
    """
    async def change_availability(self, connector_id: int, change_type: str):
        request = call.ChangeAvailabilityPayload(
                                                    connector_id = connector_id, 
                                                    type = change_type
                                                )
        response = await self.call(request)
        return response

    async def trigger_message(self,requested_message : str, connector_id: int):
        request = call.TriggerMessagePayload(
                                                    requested_message = requested_message,
                                                    connector_id = connector_id
                                                )
        response = await self.call(request)
        return response  

    async def unlock_connector(self, connector_id: int):
        request = call.UnlockConnectorPayload(
                                                    connector_id = connector_id
                                                )
        response = await self.call(request)
        return response  

    