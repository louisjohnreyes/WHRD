document.addEventListener('DOMContentLoaded', function() {

    const loadingDiv = document.getElementById('loading');
    const mainContentDiv = document.getElementById('main-content');

    function updateStatus() {
        fetch('/api/status')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if(loadingDiv.style.display !== 'none') {
                    loadingDiv.style.display = 'none';
                    mainContentDiv.classList.remove('hidden');
                }

                updateElement('mode', data.mode);
                updateElement('stage', data.stage);
                updateElement('temperature', data.temperature.toFixed(1));
                updateElement('target_temp', data.target_temp.toFixed(1));
                updateElement('max_temp', data.max_temp.toFixed(1));
                updateElement('humidity', data.humidity.toFixed(1));
                updateElement('fan_on', data.fan_on ? 'ON' : 'OFF', data.fan_on);
                updateElement('dehumidifier_on', data.dehumidifier_on ? 'ON' : 'OFF', data.dehumidifier_on);
                updateElement('fan_on_2', data.fan_on_2 ? 'ON' : 'OFF', data.fan_on_2);
                updateElement('dehumidifier_on_2', data.dehumidifier_on_2 ? 'ON' : 'OFF', data.dehumidifier_on_2);
                updateElement('buzzer_on', data.buzzer_on ? 'ON' : 'OFF', data.buzzer_on);

                const uptime_hours = Math.floor(data.uptime / 3600);
                const uptime_minutes = Math.floor((data.uptime % 3600) / 60);
                const uptime_seconds = Math.floor(data.uptime % 60);
                updateElement('uptime', `${uptime_hours.toString().padStart(2, '0')}:${uptime_minutes.toString().padStart(2, '0')}:${uptime_seconds.toString().padStart(2, '0')}`);
                updateElement('current_time', data.current_time);

                if (data.mode === 'AUTO') {
                    const minutes = Math.floor(data.remaining_seconds / 60);
                    const seconds = Math.floor(data.remaining_seconds % 60);
                    updateElement('next_temp_increase', `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
                } else {
                    updateElement('next_temp_increase', 'N/A');
                }

                // Disable manual controls in AUTO mode
                const isAutoMode = data.mode === 'AUTO';
                document.getElementById('toggle-fan').disabled = isAutoMode;
                document.getElementById('toggle-dehumidifier').disabled = isAutoMode;
            })
            .catch(error => {
                console.error('Error fetching status:', error);
                // Optionally, display an error message to the user
            });
    }

    function updateElement(id, value, activeState) {
        const element = document.getElementById(id);
        if (element && element.textContent !== value) {
            element.textContent = value;
            // Optional: Add a class for animation
            element.parentElement.classList.add('updated');
            setTimeout(() => {
                element.parentElement.classList.remove('updated');
            }, 500);
        }
        if (activeState !== undefined) {
             if(activeState) {
                element.parentElement.classList.add('active');
             } else {
                element.parentElement.classList.remove('active');
             }
        }
    }

    function createRipple(event) {
        const button = event.currentTarget;

        const circle = document.createElement("span");
        const diameter = Math.max(button.clientWidth, button.clientHeight);
        const radius = diameter / 2;

        circle.style.width = circle.style.height = `${diameter}px`;
        circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
        circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
        circle.classList.add("ripple");

        const ripple = button.getElementsByClassName("ripple")[0];

        if (ripple) {
            ripple.remove();
        }

        button.appendChild(circle);
    }

    const buttons = document.querySelectorAll('.controls button');
    buttons.forEach(button => {
        button.addEventListener('click', createRipple);
    });

    document.getElementById('toggle-mode').addEventListener('click', () => {
        fetch('/api/mode', { method: 'POST' })
            .then(() => updateStatus());
    });

    document.getElementById('next-stage').addEventListener('click', () => {
        fetch('/api/stage', { method: 'POST' })
            .then(() => updateStatus());
    });

    document.getElementById('toggle-fan').addEventListener('click', () => {
        fetch('/api/fan', { method: 'POST' })
            .then(() => updateStatus());
    });

    document.getElementById('toggle-dehumidifier').addEventListener('click', () => {
        fetch('/api/dehumidifier', { method: 'POST' })
            .then(() => updateStatus());
    });

    setInterval(updateStatus, 2000);
    updateStatus();
});