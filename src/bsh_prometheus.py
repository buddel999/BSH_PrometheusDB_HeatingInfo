# Script for providing bosch smart home heating related data to a prometheus database.
# Python Version: 3.9
# -*- coding: utf-8 -*-

from time import sleep
from boschshcpy import SHCSession, services_impl
from prometheus_client import Gauge, Enum, start_http_server
from room import RoomData

def setupRooms(session: SHCSession) -> list:
    rooms = []
    for room in session.rooms:
        tmpRoom = RoomData()
        tmpRoom.roomID = room.id
        tmpRoom.roomName = room.name
        tmpRoom.temperatureGauge = Gauge(room.id + "Temp", "The temperature of the room " + room.name + " in celsius.", ["device"])
        tmpRoom.temperatureSetGauge = Gauge(room.id + "TempSet", "The temperature set for the room " + room.name + " in celsius.", ["device"])       
        tmpRoom.valveTappetGauge = Gauge(room.id + "Valve", "The valve tappet of the room " + room.name + " in percent.", ["device"])
        tmpRoom.humidityGauge = Gauge(room.id + "Humid", "The humidity of the room " + room.name + " in percent.", ["device"])
        tmpRoom.doorWindowInfo = Enum(room.id + "DWI", "The status of doors and windows in the room " + room.name + ".", ["device"],states=["open", "closed", "unknown"])
        rooms.append(tmpRoom)
    return rooms

def getRoom(rooms: list, roomId: str) -> RoomData:
    for room in rooms:
        if room.roomID == roomId:
            return room
    return None


if __name__ == "__main__":
    BSH_CONTROLLER_IP = "192.168.x.x" #Change to your smart home controller ip.
    CERT_PATH = "./cert.pem"   #Change to the path of your registered certificate.
    KEY_PATH = "./key.pem"     #Change to the path of your registered key.
    INTERVAL = 30                     #The interval in which the scripts polls the data from the controller.
    PROMETHEUS_PORT = 9999            #The port of the prometheus client


    print("Setting up session with smart home controller...")
    session = SHCSession(controller_ip=BSH_CONTROLLER_IP, certificate=CERT_PATH, key=KEY_PATH)
    session.information.summary()

    rooms = setupRooms(session)

    print("Starting prometheus client at port 9095...")
    start_http_server(PROMETHEUS_PORT)
    print("Running (Requesting every", INTERVAL, "Seconds)...")
    while True:

        for device in session.devices:
            tmpRoom = getRoom(rooms, device.room_id)

            if device.device_service("AirQualityLevel") != None:
                device.device_service("AirQualityLevel").short_poll()
                tmpRoom.temperatureGauge.labels(device.name).set(device.device_service("AirQualityLevel").temperature)
                tmpRoom.humidityGauge.labels(device.name).set(device.device_service("AirQualityLevel").humidity)
                continue

            if device.device_service("TemperatureLevel") != None:
                device.device_service("TemperatureLevel").short_poll()
                tmpRoom.temperatureGauge.labels(device.name).set(device.device_service("TemperatureLevel").temperature)

            if device.device_service("RoomClimateControl") != None:
                device.device_service("RoomClimateControl").short_poll()
                tmpRoom.temperatureSetGauge.labels(device.name).set(device.device_service("RoomClimateControl").state["setpointTemperature"])

            if device.device_service("ValveTappet") != None:
                device.device_service("ValveTappet").short_poll()
                tmpRoom.valveTappetGauge.labels(device.name).set(device.device_service("ValveTappet").position)

            if device.device_service("HumidityLevel") != None:
                device.device_service("HumidityLevel").short_poll()
                tmpRoom.humidityGauge.labels(device.name).set(device.device_service("HumidityLevel").humidity)

            if device.device_service("ShutterContact") != None:
                device.device_service("ShutterContact").short_poll()
                if device.device_service("ShutterContact").value == services_impl.ShutterContactService.State.OPEN:
                    tmpRoom.doorWindowInfo.labels(device.name).state("open")
                elif device.device_service("ShutterContact").value == services_impl.ShutterContactService.State.CLOSED:
                    tmpRoom.doorWindowInfo.labels(device.name).state("closed")
                else:
                    tmpRoom.doorWindowInfo.labels(device.name).state("unknown")

        sleep(INTERVAL)

