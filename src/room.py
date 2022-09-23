#Class for organizing the room with the corresponding prometheus metrics

class RoomData():
    roomID = ""
    roomName = ""
    temperatureGauge = None
    valveTappetGauge = None
    humidityGauge = None
    doorWindowInfo = None
