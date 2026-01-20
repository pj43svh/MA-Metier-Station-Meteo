function updateData() {

    fetch('/api/temperature1')
        .then(response => response.text())
        .then(text => {
            console.log("Temp1:", text);
            if (text === "NULL") {
                document.getElementById('temperature1').textContent = '-- °C';
            } else {
                document.getElementById('temperature1').textContent = text + ' °C';
        }
    });

    fetch('/api/pressure1')
        .then(response => response.text())
        .then(text => {
            document.getElementById('pressure1').textContent = text + ' hPa';
    });


    fetch('/api/humidity1')
        .then(response => response.text())
        .then(text => {
            document.getElementById('humidity1').textContent = text + ' %';
    });



    fetch('/api/temperature2')
        .then(response => response.text())
        .then(text => {
            document.getElementById('temperature2').textContent = text + ' °C';
    });

    fetch('/api/pressure2')
        .then(response => response.text())
        .then(text => {
            document.getElementById('pressure2').textContent = text + ' hPa';
    });


    fetch('/api/humidity2')
        .then(response => response.text())
        .then(text => {
            document.getElementById('humidity2').textContent = text + ' %';
    });


}
// Met à jour dès le chargement
updateData();
// Met à jour toutes les 10 secondes
setInterval((updateData), 10000);
