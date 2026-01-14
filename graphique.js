const temperature = document.getElementById('graf_temperature'); // il faut mettre le bon id du canvas
const pluie = document.getElementById('graf_pluie'); // il faut mettre le bon id du canvas


//graphique de la température
const jours =['Mer', 'Jeu', 'Ven', 'Sam', 'Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim', 'Lun', 'Mar', 'Mer']; 

const data_temperature = [7, 5, 4, 5, 5, 6, 5, 4, 5, 4, 5, 5, 6, 5, 4];

new Chart(temperature, { // copier coller le code de température ici en mettant les bons paramètres
  type: 'bar',
  data: {
    labels: jours, // ici, ce sont les noms de la donnée 
    datasets: [{
      label: 'Température en °C',
      data: data_temperature, // ici, c'est la données
      backgroundColor: [
        'rgba(223, 93, 18, 0.47)' // orange clair
      ],
      borderColor: [
        'rgba(223, 93, 18, 1)' // orange foncé
      ],
      borderWidth: 1
    }]
  },
  options: {
    plugins: {
      legend: {
        labels: {
          color: '#f19265ff', // Couleur des labels de la légende
          font: {
            size: 14
          }
        }
      },
      title: {
        display: true,
        text: 'Température',
        color: '#eb6936ff', // Couleur du titre
        font: {
          size: 24
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#dadadaff' // Couleur des labels de l'axe X
        }
      },
      y: {
        ticks: {
          color: '#dadadaff' // Couleur des labels de l'axe Y
        }
      }
    }
  }
});

//graphique de la pluie
const data_pluie = [0, 0, 2, 12, 0, 0, 3, 1, 5, 10, 0, 0, 2, 5, 1];

new Chart(pluie, {
  type: 'bar',
  data: {
    labels: jours, // ici, ce sont les noms de la donnée
    datasets: [{
      label: 'Volume en millimètres',
      data: data_pluie, // ici, c'est la données
      backgroundColor: [
        'rgba(54, 163, 235, 0.47)' // bleu clair
      ],
      borderColor: [
        'rgba(54, 162, 235, 1)' // bleu foncé
      ],
      borderWidth: 1
    }]
  },
  options: {
    plugins: {
      legend: {
        labels: {
          color: '#7bc2f1ff', // Couleur des labels de la légende
          font: {
            size: 14
          }
        }
      },
      title: {
        display: true,
        text: 'Taux de pluie',
        color: '#36a2eb', // Couleur du titre
        font: {
          size: 24
        }
      }
    },
    scales: {
      x: {
        ticks: {
          color: '#dadadaff' // Couleur des labels de l'axe X
        }
      },
      y: {
        ticks: {
          color: '#dadadaff' // Couleur des labels de l'axe Y
        }
      }
    }
  }
});

//graphique du temps
const temps = document.getElementById('graf_temps').getContext('2d');

// Données réelles de la semaine (à adapter selon tes données)
const weatherData = {
    'Soleil': 2,
    'Pluie': 2,
    'Nuageux': 2,
    'Orage': 1,
    'Neige': 3
};

const labels_temps = Object.keys(weatherData);
const data_temps = Object.values(weatherData);

// Couleurs personnalisées (tu peux les changer)
const colors = [
    '#FFD700', // Soleil (jaune doré)
    '#1296d3ff', // Pluie (bleu ciel)
    '#a3a3a3ff', // Nuageux (gris)
    '#7e3d00ff',  // Orage (rouge foncé)
    '#9ed9ecff'  // Neige (bleu clair)
];

new Chart(temps, {
    type: 'doughnut',
    data: {
        labels: labels_temps,
        datasets: [{
            data: data_temps,
            backgroundColor: colors,
            borderColor: '#ffffff',
            borderWidth: 2
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    color: '#dadadaff',
                    font: {
                        size: 14
                    }
                }
            },
            title: {
                display: true,
                text: 'Météo de la semaine',
                color: '#c6e5f1ff',
                font: {
                    size: 24
                }
            }
        }
    }
});