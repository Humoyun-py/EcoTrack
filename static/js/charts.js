
"""
Charts.js - Statistik diagrammalar uchun
"""

charts_js_content = """
// Progress diagrammalari
function initProgressCharts() {
    // Haftalik progress diagrammasi
    const weeklyCtx = document.getElementById('weeklyProgressChart');
    if (weeklyCtx) {
        const weeklyChart = new Chart(weeklyCtx, {
            type: 'line',
            data: {
                labels: ['Du', 'Se', 'Ch', 'Pa', 'Ju', 'Sh', 'Ya'],
                datasets: [{
                    label: 'Kunlik Ballar',
                    data: [12, 19, 15, 25, 22, 30, 28],
                    borderColor: '#2ecc71',
                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Haftalik Progress'
                    }
                }
            }
        });
    }
    
    // Topshiriq turlari bo'yicha diagramma
    const tasksCtx = document.getElementById('tasksChart');
    if (tasksCtx) {
        const tasksChart = new Chart(tasksCtx, {
            type: 'doughnut',
            data: {
                labels: ['Plastik', 'Suv', 'Eneriya', 'Qayta ishlash', "Daraxt"],
                datasets: [{
                    data: [30, 25, 20, 15, 10],
                    backgroundColor: [
                        '#2ecc71',
                        '#27ae60',
                        '#16a085',
                        '#1abc9c',
                        '#3498db'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// DOM yuklanganida diagrammalarni ishga tushirish
document.addEventListener('DOMContentLoaded', function() {
    initProgressCharts();
});
"""