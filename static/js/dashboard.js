function completeTask(taskId, points) {
    const button = event.target;
    button.disabled = true;
    button.textContent = '⏳...';

    fetch('/complete_task', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            task_id: taskId,
            points: points
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.textContent = '✅ Bajarildi';
            button.style.backgroundColor = '#27ae60';
            
            // Sahifani yangilash
            setTimeout(() => {
                location.reload();
            }, 1000);
            
            if (data.badge_earned) {
                alert(`Tabriklaymiz! Siz "${data.badge_earned}" yutuq medalini qo'lga kiritdingiz! 🎉`);
            }
        }
    })
    .catch(error => {
        console.error('Xatolik:', error);
        button.disabled = false;
        button.textContent = '✅ Bajardim';
        alert('Topshiriqni bajarishda xatolik yuz berdi. Iltimos, qayta urinib ko\'ring.');
    });
}