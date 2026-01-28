let temperatureChart = null;
let pressureChart = null;
let humidityChart = null;


async function loadStatictical(data_type, dateFilter = "today") {
    const url = `/api/statistical?type=${data_type}&date=${dateFilter}`;
    const response = await fetch(url);
    const data = await response.json();
    console.log(data)
    return data;
}



async function fetchTemperatureData(date_selected = "today") {
    const json_temp = await loadStatictical("temperature", dateFilter = date_selected);
    let labels = json_temp.hours;
    let datas1 = json_temp.data1;
    let datas2 = json_temp.data2;

    const temperature = document.getElementById('temperature');

    temperatureChart = new Chart(temperature, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Sensor 1',
                    data: datas1,
                    borderColor: 'rgba(0, 162, 255, 1)',
                    tension: 0.1
                },
                {
                    label: 'Sensor 2',
                    data: datas2,
                    borderColor: 'rgba(245, 24, 72, 1)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
    maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: 'rgba(53, 53, 53, 1)'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Hours',
                        color: 'rgba(53, 53, 53, 1)'
                    },
                    ticks: {
                        color: 'rgba(53, 53, 53, 1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '°C',
                        color: 'rgba(53, 53, 53, 1)'
                    },
                    ticks: {
                        color: 'rgba(53, 53, 53, 1)'
                    },
                    min: 0

                }
            }
        }
    });
}

async function fetchPressureData(date_selected = "today") {
    const json_temp = await loadStatictical("pressure", dateFilter = date_selected);
    let labels = json_temp.hours;
    let datas1 = json_temp.data1;
    let datas2 = json_temp.data2;

    const pressure = document.getElementById('pressure');

    pressureChart = new Chart(pressure, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Sensor 1',
                    data: datas1,
                    borderColor: 'rgba(0, 162, 255, 1)',
                    tension: 0.1,
                },
                {
                    label: 'Sensor 2',
                    data: datas2,
                    borderColor: 'rgba(245, 24, 72, 1)',
                    tension: 0.1
                }
            ]
        },
        options: {
            responsive: true,
    maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        color: 'rgba(53, 53, 53, 1)'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Hours',
                        color: 'rgba(53, 53, 53, 1)'
                    },
                    ticks: {
                        color: 'rgba(53, 53, 53, 1)'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '°C',
                        color: 'rgba(53, 53, 53, 1)'
                    },
                    ticks: {
                        color: 'rgba(53, 53, 53, 1)'
                    },
                    min: 850

                }
            }
        }
    });
}

async function fetchHumidityData(date_selected = "today") {
    const json_temp = await loadStatictical("humidity", dateFilter = date_selected);
    let labels = json_temp.hours;
    let datas1 = json_temp.data1;
    let datas2 = json_temp.data2;

    const humidity = document.getElementById('humidity');

    humidityChart = new Chart(humidity, {
    type: 'bar',
    data: {
        labels: labels,
        datasets: [
            {
                label: 'Sensor 1',
                data: datas1,
                backgroundColor: 'rgba(0, 162, 255, 1)'
            },
            {
                label: 'Sensor 2',
                data: datas2,
                backgroundColor: 'rgba(245, 24, 72, 1)'
            }
        ]
    },
    options: {
    responsive: true,
    maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    color: 'rgba(53, 53, 53, 1)'
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
            }
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: 'Hours',
                    color: 'rgba(53, 53, 53, 1)'
                },
                ticks: {
                    color: 'rgba(53, 53, 53, 1)'
                }
            },
            y: {
                title: {
                    display: true,
                    text: '%',
                    color: 'rgba(53, 53, 53, 1)'
                },
                ticks: {
                    color: 'rgba(53, 53, 53, 1)'
                },
                min: 0,
                max:100
            }
        }
    }
});
};

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

async function updateTemperature(date_selected="today") {
    const json_temp = await loadStatictical("temperature", dateFilter = date_selected);
    let labels = json_temp.hours;
    let datas1 = json_temp.data1;
    let datas2 = json_temp.data2;
    temperatureChart.data.labels = labels;
    temperatureChart.data.datasets[0].data = datas1;
    temperatureChart.data.datasets[1].data = datas2;
    temperatureChart.update();
}

async function updatePressure(date_selected="today") {
    const json_pres = await loadStatictical("pressure", dateFilter = date_selected);
    let labels = json_pres.hours;
    let datas1 = json_pres.data1;
    let datas2 = json_pres.data2;
    pressureChart.data.labels = labels;
    pressureChart.data.datasets[0].data = datas1;
    pressureChart.data.datasets[1].data = datas2;
    pressureChart.update();
}

async function updateHumidity(date_selected="today") {
    const json_humi = await loadStatictical("humidity", dateFilter = date_selected);
    let label = json_humi.hours;
    let datas1 = json_humi.data1;
    let datas2 = json_humi.data2;
    humidityChart.data.labels = label;
    humidityChart.data.datasets[0].data = datas1;
    humidityChart.data.datasets[1].data = datas2;
    humidityChart.update();
}

let date_selected = "today";

async function refresh_date() {
    const select_list = document.getElementById("date");
    console.log("button pressed ", select_list.value);
    date_selected = document.getElementById("date").value;
    updateTemperature(date_selected);
    updatePressure(date_selected);
    updateHumidity(date_selected);
}

// Attacher l'événement au bouton, si présent
const refreshBtn = document.getElementById("refresh_btn");
if (refreshBtn) {
    refreshBtn.addEventListener("click", refresh_date);
}
document.addEventListener('DOMContentLoaded', () => {
    fetchTemperatureData();
    fetchPressureData();
    fetchHumidityData();
    loadDates(); // Charger les dates au chargement
});

// petit script inutile pour rendre le bouton swag
document.querySelectorAll('input[type=button]').forEach(button => {
    button.addEventListener('click', function () {
        this.classList.add('jello');
        // Supprime la classe après la fin de l'animation pour permettre une nouvelle animation
        this.addEventListener('animationend', function () {
            this.classList.remove('jello');
        }, { once: true });
    });
});

setInterval(() => updateTemperature(date_selected = date_selected), 20000);
setInterval(() => updatePressure(date_selected = date_selected), 20000);
setInterval(() => updateHumidity(date_selected = date_selected), 20000);