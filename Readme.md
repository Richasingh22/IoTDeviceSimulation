# IoT Devices Simulator

This is a simple IoT devices simulator that can be used to test the sending messages from apps to IoT devices without actual hardware.


# Usage
    python3 -m venv venv

    source venv/bin/activate      # For bash/zsh (MacOS/Linux)
    source venv/bin/activate.fish # For fish
    source venv/bin/activate.csh  # For csh/tcsh
    venv\Scripts\activate.bat     # For CMD (Windows)
    venv\Scripts\Activate.ps1     # For PowerShell (Windows)
    
    python3 -m pip install -r requirements.txt

    python3 Simulator.py

Go to http://localhost:5000/ to see the simulator.

# All Endpoints

**Type**| **Endpoint**|**Description**
:-----:|:-----:|:-----:
`GET`| `/`| Returns the Simulation webpage page
`GET`| `/controller`| Returns the Simulation Controller webpage page
`POST`| `/controller`| Sends a message to the device

# Postman requests
> Endpoint  `/user/device/control`

`Use the following payload (Body: RAW - JSON) to send a message to the device:`

    {
        "username": "rich",
        "room": "master",
        "lightIntensity": "20",
        "thermostatTemperature": "1",
        "thermostatMode": "1",
        "curtainPercentage": "1"
    }

## Payload Parameters:

> `username`: username of the user (REQUIRED)

> `room`: room of the user (REQUIRED)

> `lightIntensity`: light intensity of the room

> `thermostatTemperature`: thermostat temperature of the room

> `thermostatMode`: thermostat mode of the room

> `curtainPercentage`: curtain open percentage of the room


## Request Response:

> `200`: OK

    {
        "status": "Success",
        "message": "Successfully updated devices",
        "username": "rich",
        "room": "master",
        "usedConfig": {
            "light": {
                "lightIntensity": "20",
                "status": "Success"
            }
        }
    }

> `200`: OK `[Partial Success]`

    {
        "status": "Partial Success",
        "message": "Successfully few devices",
        "username": "rich",
        "room": "master",
        "usedConfig": {
            "light": {
                "lightIntensity": "-1",
                "status": "Failed",
                "message": "lightIntensity must be between 0 and 100"
            },
            "thermostat": {
                "thermostatTemperature": "1",
                "thermostatMode": "1",
                "status": "Success"
            },
            "curtain": {
                "curtainPercentage": "1",
                "status": "Success"
            }
        }
    }

> `400`: Bad Request

    {
        "status": "Failed", 
        "message": "Username is required"
    }

> `400`: Bad Request

    {
        "status": "Failed", 
        "message": "Room is required"
    }

> `400`: Bad Request [All Device Updates failed]

    {
        "status": "Failed",
        "message": "Failed to update devices",
        "username": "rich",
        "room": "master",
        "usedConfig": {
            "light": {
                "lightIntensity": "-1",
                "status": "Failed",
                "message": "lightIntensity must be between 0 and 100"
            },
            "thermostat": {
                "thermostatTemperature": "-50",
                "thermostatMode": "-1",
                "status": "Failed",
                "message": "Temperature is out of range"
            },
            "curtain": {
                "curtainPercentage": "-1",
                "status": "Failed",
                "message": "Curtain Open Percentage must be between 0 and 100"
            }
        }
    }