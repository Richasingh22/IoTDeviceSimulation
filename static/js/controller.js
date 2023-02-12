// show overlay
function showOverlay(sec) {
    document.getElementsByClassName("overlay")[0].style.display = "block";
    setTimeout(function () {
        document.getElementsByClassName("overlay")[0].style.display = "none";
    }, sec * 1000);
}

// on light switch change send request to server
document.getElementById("lightIntensity").addEventListener("change", function () {
    var lightIntensity = document.getElementById("lightIntensity").value;
    var curtainPercentage = document.getElementById("curtainPercentage").value;
    var thermostatMode = document.getElementById("thermostatMode").value;
    var thermostatTemperature = document.getElementById("thermostatTemperature").value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/controller", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let resp = JSON.parse(xhr.response);
            if (resp['status'] == "Partial Success") {
                if(resp['usedConfig']['light']['status'] == "Failed") {
                    alert("Error: Failed Updating light intensity!\n" + xhr.response);
                }
            }
        }
        if (xhr.readyState === 4 && xhr.status === 400) {
            alert("Error:\n" + xhr.response);
        }
    };
    xhr.send(JSON.stringify({
        "username": USERNAME,
        "room": ROOM,
        "lightIntensity": lightIntensity,
        "curtainPercentage": curtainPercentage,
        "thermostatMode": thermostatMode,
        "thermostatTemperature": thermostatTemperature
    }));

    setTimeout(function () {
        showOverlay(overLayTime);
    }, 800);
});

// on curtain Percentage change send request to server
document.getElementById("curtainPercentage").addEventListener("change", function () {
    var curtainPercentage = document.getElementById("curtainPercentage").value;
    var lightIntensity = document.getElementById("lightIntensity").value;
    var thermostatMode = document.getElementById("thermostatMode").value;
    var thermostatTemperature = document.getElementById("thermostatTemperature").value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/controller", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let resp = JSON.parse(xhr.response);
            if (resp['status'] == "Partial Success") {
                if(resp['usedConfig']['light']['status'] == "Failed") {
                    alert("Error: Failed Updating Thermostat Temperarture!\n" + xhr.response);
                }
            }
        }
        if (xhr.readyState === 4 && xhr.status === 400) {
            alert("Error:\n" + xhr.response);
        }
    };
    xhr.send(JSON.stringify({
        "username": USERNAME,
        "room": ROOM,
        "lightIntensity": lightIntensity,
        "curtainPercentage": curtainPercentage,
        "thermostatMode": thermostatMode,
        "thermostatTemperature": thermostatTemperature
    }));
    showOverlay(overLayTime);
});

// on temperature change send request to server
document.getElementById("thermostatMode").addEventListener("change", function () {
    var lightIntensity = document.getElementById("lightIntensity").value;
    var curtainPercentage = document.getElementById("curtainPercentage").value;
    var thermostatMode = document.getElementById("thermostatMode").value;
    var thermostatTemperature = document.getElementById("thermostatTemperature").value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/controller", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = () => {
        if (xhr.readyState === 4 && xhr.status === 200) {
            let resp = JSON.parse(xhr.response);
            if (resp['status'] == "Partial Success") {
                if(resp['usedConfig']['light']['status'] == "Failed") {
                    alert("Error: Failed Updating Thermostat Mode!\n" + xhr.response);
                }
            }
        }
        if (xhr.readyState === 4 && xhr.status === 400) {
            alert("Error:\n" + xhr.response);
        }
    };
    xhr.send(JSON.stringify({
        "username": USERNAME,
        "room": ROOM,
        "lightIntensity": lightIntensity,
        "curtainPercentage": curtainPercentage,
        "thermostatMode": thermostatMode,
        "thermostatTemperature": thermostatTemperature
    }));
    showOverlay(overLayTime);
});

// on temperature change send request to server
document.getElementById("thermostatTemperature").addEventListener("change", function () {
    var lightIntensity = document.getElementById("lightIntensity").value;
    var curtainPercentage = document.getElementById("curtainPercentage").value;
    var thermostatMode = document.getElementById("thermostatMode").value;
    var thermostatTemperature = document.getElementById("thermostatTemperature").value;
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/controller", true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        "username": USERNAME,
        "room": ROOM,
        "lightIntensity": lightIntensity,
        "curtainPercentage": curtainPercentage,
        "thermostatMode": thermostatMode,
        "thermostatTemperature": thermostatTemperature
    }));
    showOverlay(overLayTime);
});

// set slider Light Intensity value
function rangeLightIntensitySlide(value) {
    document.getElementById('rangeLightIntensitySlideValue').innerHTML = value + "%";
}
rangeLightIntensitySlide(lightIntensity);

// set slider Curtain value
function rangeCurtainSlide(value) {
    document.getElementById('rangeCurtainValue').innerHTML = value + "%";
}
rangeCurtainSlide(curtainPercentage);

// set slider Light Intensity value
function rangeThermostatTemperatureSlide(value) {
    document.getElementById('rangeThermostatTemperatureValue').innerHTML = value + "°C";
}
rangeThermostatTemperatureSlide(thermostatTemperature);

