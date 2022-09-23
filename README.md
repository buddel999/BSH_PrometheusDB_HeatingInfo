# BSH_PrometheusDB_HeatingInfo
Script for providing bosch smart home heating related data to a prometheus database.
Originally intended to create a temperature history visualization with [Grafana](https://grafana.com/).

## Setup
To use the script simply adjust the following variables in the main portion of the script:
- ```BSH_CONTROLLER_IP```: Use it to set the IP of your Bosch smart home controller
- ```CERT_PATH```: Set the filepath of your already registered ssl certificate file
- ```KEY_PATH```: Set the filepath of your already registered ssl private key file
  - For more informations to the registering process look [here](https://github.com/BoschSmartHome/bosch-shc-api-docs/tree/master/postman#register-a-new-client-to-the-bosch-smart-home-controller)
- ```PROMETHEUS_PORT```: Port the prometheus client is going to use
- (optional)```INTERVAL```: The polling interval of the script in seconds. You can change it to match the request interval of your prometheus db 

## Collected metrics
The following metrics are collected from the bsh controller for every room in your smarthome.
In every room the data is collected from every device that is capable of providing those metrics (e.g. you have multiple heating thermostats in one room every thermostats temperature is recorded)
- Prometheus Gauge:
  - ```Temp``` - The temperature measured by a device
  - ```TempSet``` - The set temperature for the room
  - ```Valve``` - The position of the valve in a heating thermostat
  - ```Humid``` - The humidity measured by a device
- Prometheus Enum:
  - ```DWI``` - The status of door/window contacts (open | closed | unknown)
