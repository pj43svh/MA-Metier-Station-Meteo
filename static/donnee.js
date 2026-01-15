function updateTemperature() {
    fetch('/api/temperature')
        .then(response => response.text())
        .then(text => {
            document.getElementById('temperature').textContent = text + ' °C';
    });
}
function updatePression() {
    fetch('/api/pression')
        .then(response => response.text())
        .then(text => {
            document.getElementById('pression').textContent = text + ' hPa';
    });
}
function updateHumidite() {
    fetch('/api/humidite')
        .then(response => response.text())
        .then(text => {
            document.getElementById('humidite').textContent = text + ' %';
    });
}
function updateTemps() {
    fetch('/api/temps')
        .then(response => response.text())
        .then(text => {
            document.getElementById('temps').textContent = text;
    });
}
// Met à jour dès le chargement
updateTemperature();
updatePression();
updateHumidite();
updateTemps();
// Met à jour toutes les 10 secondes
setInterval((updateTemperature), 10000);
setInterval((updatePression), 10000);
setInterval((updateHumidite), 10000);
setInterval((updateTemps), 10000);