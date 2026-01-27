let date_selected = "today"; // valeur par défaut

// Fonction pour charger les données depuis l'API Flask
async function loadHistory(sensorId, dateFilter = "today") {
    try {
        const url = `/api/history${sensorId}?date=${dateFilter}`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Erreur du serveur');
        
        const data = await response.json();
        
        const { date, hour, temperature, humidity, pressure } = data;
        if (!date || !hour || !temperature || !humidity || !pressure) {
            throw new Error('Données incomplètes reçues');
        }
        
        const maxLength = Math.max(date.length, hour.length, temperature.length, humidity.length, pressure.length);
        const tbody = document.getElementById(`history${sensorId}-body`);
        tbody.innerHTML = '';
        
        
        
        for (let i = maxLength - 1; i >= 0; i--) {
            const row = document.createElement('tr');
            
            const tVal = temperature[i];
            
            row.innerHTML = `
        <td>${date[i] !== undefined ? date[i] : '—'}</td>
        <td>${hour[i] !== undefined ? hour[i] : '—'}</td>
        <td class="temp-cell">
            ${tVal !== undefined ? tVal + ' °C' : '—'}
        </td>
        <td>${humidity[i] !== undefined ? humidity[i] + ' %' : '—'}</td>
        <td>${pressure[i] !== undefined ? pressure[i] + ' hPa' : '—'}</td>
    `;
            
            const tempCell = row.querySelector('.temp-cell');
            if (tVal !== undefined && tVal !== null && !isNaN(tVal)) {
                const tempNum = Number(tVal);
                if (tempNum >= 22) {
                    tempCell.style.color = 'red';
                    tempCell.style.fontWeight = 'bold';
                } else {
                    tempCell.style.color = '';
                    tempCell.style.fontWeight = '';
                }
            }
            
            tbody.appendChild(row);
        }
        
        
    } catch (error) {
        console.error('Erreur lors du chargement de l’historique :', error);
        document.getElementById(`history${sensorId}-body`).innerHTML = `<tr><td colspan="5">Erreur : ${error.message}</td></tr>`;
    }
}


// Fonction pour charger les dates uniques depuis l'API
async function loadDates() {
    try {
        const response = await fetch('/api/dates_unique');
        if (!response.ok) throw new Error('Erreur du serveur');
        
        const dates = await response.json();
        
        const selectList = document.getElementById("date");
        
        
        // Ajouter les dates uniques
        for (const date of dates) {
            const option = document.createElement('option');
            option.value = date;
            option.textContent = date;
            selectList.appendChild(option);
        }
        
        
    } catch (error) {
        console.error('Erreur lors du chargement des dates :', error);
        const selectList = document.getElementById("date");
        selectList.innerHTML = '<option value="">Erreur</option>';
    }
}
// Fonction pour calculer (ex: avec la date sélectionnée)
async function refresh_date() {
    const select_list = document.getElementById("date");
    console.log("button pressed ", select_list.value);
    date_selected = document.getElementById("date").value;
    loadHistory("1",date_selected = date_selected);
    loadHistory("2",date_selected = date_selected);
}

// Attacher l'événement au bouton, si présent
const refreshBtn = document.getElementById("refresh_btn");
if (refreshBtn) {
    refreshBtn.addEventListener("click", refresh_date);
}
document.addEventListener('DOMContentLoaded', () => {
    loadDates(); // 👈 Charger les dates au chargement
    refresh_date();
});

// Actualiser toutes les 20 secondes
setInterval(() => loadHistory("1",date_selected = date_selected), 20000);
setInterval(() => loadHistory("2",date_selected = date_selected), 20000);