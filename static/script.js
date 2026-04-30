document.addEventListener('DOMContentLoaded', () => {
    // Dark Mode Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const body = document.body;
    
    if (localStorage.getItem('dark-mode') === 'true') {
        body.classList.add('dark-mode');
        if (themeToggle) themeToggle.innerHTML = '<i class="fas fa-sun"></i>';
    }
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            body.classList.toggle('dark-mode');
            const isDark = body.classList.contains('dark-mode');
            localStorage.setItem('dark-mode', isDark);
            themeToggle.innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
        });
    }

    // Optimization Logic
    const optimizeForm = document.getElementById('optimize-form');
    if (optimizeForm) {
        optimizeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(optimizeForm);
            const submitBtn = optimizeForm.querySelector('button[type="submit"]');
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Optimizing...';
            submitBtn.disabled = true;

            try {
                const response = await fetch('/optimize', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();
                displayResult(data);
            } catch (error) {
                showToast('Error optimizing plan', 'error');
            } finally {
                submitBtn.innerHTML = 'Optimize My Plan';
                submitBtn.disabled = false;
            }
        });
    }

    function displayResult(data) {
        if (data.error) {
            showToast('Optimization failed: ' + data.error, 'error');
            return;
        }

        const resultContainer = document.getElementById('result-container');
        const dpList = document.getElementById('dp-list');
        const addedList = document.getElementById('added-list');
        const rejectedList = document.getElementById('rejected-list');
        
        // Update Summary
        document.getElementById('res-avail-time').innerText = data.available_time + ' hrs';
        document.getElementById('res-used-time').innerText = data.used_time + ' hrs';
        document.getElementById('res-remain-time').innerText = data.remaining_time + ' hrs';
        
        const scoreEl = document.getElementById('res-total-score');
        if (scoreEl) scoreEl.innerText = data.total_score;

        dpList.innerHTML = '';
        addedList.innerHTML = '';
        rejectedList.innerHTML = '';

        const createCard = (subject, type) => {
            const card = document.createElement('div');
            card.className = `item-card item-${type} fade-in`;
            
            let icon, label, badgeClass;
            if (type === 'dp') {
                icon = 'check-double';
                label = 'Selected (Optimal)';
                badgeClass = 'badge-secondary';
            } else if (type === 'added') {
                icon = 'plus-circle';
                label = 'Added (Extra Fill)';
                badgeClass = 'badge-primary';
            } else {
                icon = 'times-circle';
                label = 'Rejected';
                badgeClass = '';
            }

            card.innerHTML = `
                <div style="font-size: 1.5rem; color: ${type === 'dp' ? 'var(--secondary)' : type === 'added' ? 'var(--primary)' : '#94a3b8'};">
                    <i class="fas fa-${icon}"></i>
                </div>
                <div style="flex-grow: 1;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <strong style="color: var(--text-light); font-size: 1.1rem;">${subject.name}</strong>
                        <span class="badge ${badgeClass}">${label} | Score: ${subject.importance}</span>
                    </div>
                    <div style="font-size: 0.9rem; color: #64748b;">
                        Time: ${subject.study_time} hrs | Efficiency: ${(subject.importance / subject.study_time).toFixed(2)}
                    </div>
                </div>
            `;
            return card;
        };

        // Render sections
        if (data.dp_selected.length > 0) {
            data.dp_selected.forEach(s => dpList.appendChild(createCard(s, 'dp')));
        } else {
            dpList.innerHTML = '<p style="color: #64748b; font-size: 0.85rem; padding: 10px;">No optimal subjects found for this time limit.</p>';
        }

        if (data.added_subjects.length > 0) {
            data.added_subjects.forEach(s => addedList.appendChild(createCard(s, 'added')));
        } else {
            addedList.innerHTML = '<p style="color: #64748b; font-size: 0.85rem; padding: 10px;">No additional subjects could fit.</p>';
        }

        if (data.rejected_subjects.length > 0) {
            data.rejected_subjects.forEach(s => rejectedList.appendChild(createCard(s, 'rejected')));
        }

        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
        showToast('Advanced plan generated!', 'success');
    }

    // Toast Notification
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} show`;
        toast.innerText = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // Charts (if on dashboard/admin)
    const ctx = document.getElementById('studyChart');
    if (ctx) {
        const subjects = JSON.parse(document.getElementById('subjects-data').textContent);
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: subjects.map(s => s.name),
                datasets: [{
                    label: 'Importance',
                    data: subjects.map(s => s.importance),
                    backgroundColor: '#4f46e5',
                    borderRadius: 8
                }, {
                    label: 'Study Time (hrs)',
                    data: subjects.map(s => s.study_time),
                    backgroundColor: '#22c55e',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    }
});
