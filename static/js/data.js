function updateData() {

    fetch('/api/temperature1')
        .then(response => response.text())
        .then(text => {
            if (text === "NULL") {
                document.getElementById('temperature1').textContent = '-- °C';
            } else {
                document.getElementById('temperature1').textContent = text + ' °C';
            }
        });

    fetch('/api/pressure1')
        .then(response => response.text())
        .then(text => {
            if (text === "NULL") {
                document.getElementById('pressure1').textContent = '-- hPa';
            } else {
                document.getElementById('pressure1').textContent = text + ' hPa';
            }
        });

    fetch('/api/humidity1')
        .then(response => response.text())
        .then(text => {
            if (text === "NULL") {
                document.getElementById('humidity1').textContent = '-- %';
            } else {
                document.getElementById('humidity1').textContent = text + ' %';
            }
        });


    fetch('/api/temperature2')
        .then(response => response.text())
        .then(text => {
            if (text === "NULL") {
                document.getElementById('temperature2').textContent = '-- °C';
            } else {
                document.getElementById('temperature2').textContent = text + ' °C';
            }
        });

    fetch('/api/pressure2')
        .then(response => response.text())
        .then(text => {
            if (text === "NULL") {
                document.getElementById('pressure2').textContent = '-- hPa';
            } else {
                document.getElementById('pressure2').textContent = text + ' hPa';
            }
        });

    fetch('/api/humidity2')
        .then(response => response.text())
        .then(text => {
            if (text === "NULL") {
                document.getElementById('humidity2').textContent = '-- %';
            } else {
                document.getElementById('humidity2').textContent = text + ' %';
            }
        });
}
// Met à jour dès le chargement
updateData();
// Met à jour toutes les 20 secondes
setInterval((updateData), 20000);
