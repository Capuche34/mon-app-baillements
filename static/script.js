document.addEventListener("DOMContentLoaded", () => {
    const toggleButton = document.getElementById("darkModeToggle");
    const body = document.body;

    // Vérifier le mode enregistré
    if (localStorage.getItem("dark-mode") === "enabled") {
        body.classList.add("dark-mode");
        toggleButton.textContent = "☀️";
    }

    toggleButton.addEventListener("click", () => {
        body.classList.toggle("dark-mode");

        if (body.classList.contains("dark-mode")) {
            localStorage.setItem("dark-mode", "enabled");
            toggleButton.textContent = "☀️";
        } else {
            localStorage.setItem("dark-mode", "disabled");
            toggleButton.textContent = "🌙";
        }
    });

    // Script pour le changement d'onglet
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetId = this.id.replace('-tab', '-content');

            tabContents.forEach(content => {
                content.classList.remove('active');
            });

            document.getElementById(targetId).classList.add('active');
        });
    });

    // Script pour générer les graphiques des bâillements
    if (window.graphData) {
        const graphData = window.graphData;
        const labels = Array.from({length: 18}, (_, i) => `${i + 7}h`);

        const createChart = (ctx, data) => {
            new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        data: data.map(hour => ({ x: hour, y: 0 })),
                        backgroundColor: 'rgba(99, 132, 255, 1)',
                        pointRadius: 5
                    }]
                },
                options: {
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            type: 'linear',
                            position: 'bottom',
                            min: 7,
                            max: 24,
                            ticks: {
                                stepSize: 1,
                                autoSkip: false,
                                maxTicksLimit: 18,
                                callback: function(value) {
                                    if (value >= 7 && value <= 24) {
                                        return `${value}h`;
                                    }
                                    return '';
                                }
                            }
                        },
                        y: {
                            display: false
                        }
                    },
                    layout: {
                        padding: {
                            left: 20,
                            right: 20
                        }
                    }
                }
            });
        };

        createChart(document.getElementById('chartToday').getContext('2d'), graphData[Object.keys(graphData)[2]]);
        createChart(document.getElementById('chartYesterday').getContext('2d'), graphData[Object.keys(graphData)[1]]);
        createChart(document.getElementById('chartDayBeforeYesterday').getContext('2d'), graphData[Object.keys(graphData)[0]]);
    }
});

// Définir graphData dans le contexte global
window.graphData = JSON.parse(document.getElementById('graphData').textContent);