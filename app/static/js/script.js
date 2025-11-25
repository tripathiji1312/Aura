/* --- AURA: CINEMATIC CORE --- */

// --- CONFIG ---
const BASE_URL = "";
let currentUserId = null;
let chartInstance = null;

// --- TOOLTIP SYSTEM (Fixed z-index) ---
(function initTooltips() {
    // Create tooltip container
    const tooltipEl = document.createElement('div');
    tooltipEl.className = 'tooltip-container';
    document.body.appendChild(tooltipEl);
    
    let hideTimeout;
    
    document.addEventListener('mouseenter', (e) => {
        const target = e.target.closest('[data-tooltip]');
        if (!target) return;
        
        clearTimeout(hideTimeout);
        
        const text = target.getAttribute('data-tooltip');
        const pos = target.getAttribute('data-tooltip-pos') || 'top';
        
        tooltipEl.textContent = text;
        tooltipEl.className = 'tooltip-container tooltip-' + pos;
        
        // Get element position
        const rect = target.getBoundingClientRect();
        const tooltipRect = tooltipEl.getBoundingClientRect();
        
        let top, left;
        
        if (pos === 'bottom') {
            top = rect.bottom + 10;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        } else {
            // Default to top
            top = rect.top - tooltipRect.height - 10;
            left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        }
        
        // Keep within viewport
        if (left < 10) left = 10;
        if (left + tooltipRect.width > window.innerWidth - 10) {
            left = window.innerWidth - tooltipRect.width - 10;
        }
        if (top < 10) {
            top = rect.bottom + 10;
            tooltipEl.className = 'tooltip-container tooltip-bottom';
        }
        
        tooltipEl.style.top = top + 'px';
        tooltipEl.style.left = left + 'px';
        tooltipEl.classList.add('visible');
    }, true);
    
    document.addEventListener('mouseleave', (e) => {
        const target = e.target.closest('[data-tooltip]');
        if (!target) return;
        
        hideTimeout = setTimeout(() => {
            tooltipEl.classList.remove('visible');
        }, 100);
    }, true);
})();

// Check for saved login on page load
function checkSavedLogin() {
    const savedUserId = localStorage.getItem('aura_user_id');
    if (savedUserId) {
        currentUserId = savedUserId;
        return true;
    }
    return false;
}

// Logout function
function handleLogout() {
    currentUserId = null;
    localStorage.removeItem('aura_user_id');
    localStorage.removeItem('aura_user_name');
    showToast('success', 'Logged Out', 'You have been successfully logged out.');
    navigateTo('landing');
}

// --- TOAST NOTIFICATION SYSTEM ---
function showToast(type, title, message, duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: 'ri-checkbox-circle-fill',
        error: 'ri-error-warning-fill',
        warning: 'ri-alert-fill',
        info: 'ri-information-fill'
    };

    toast.innerHTML = `
        <div class="toast-icon">
            <i class="${icons[type] || icons.info}"></i>
        </div>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="ri-close-line"></i>
        </button>
        <div class="toast-progress" style="animation: toastProgress ${duration}ms linear forwards;"></div>
    `;

    container.appendChild(toast);

    // Trigger show animation
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Auto remove
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hiding');
        setTimeout(() => toast.remove(), 400);
    }, duration);

    return toast;
}

// --- GSAP & LENIS INIT ---
gsap.registerPlugin(ScrollTrigger);

const lenis = new Lenis({
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
    direction: 'vertical',
    gestureDirection: 'vertical',
    smooth: true,
    mouseMultiplier: 1,
    smoothTouch: false,
    touchMultiplier: 2,
});

function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// --- ANIMATION FUNCTIONS ---
function initHeroAnimations() {
    const tl = gsap.timeline();

    // Split text animation (Corrected Selector)
    tl.from('.hero-subtitle', {
        y: 20,
        opacity: 0,
        duration: 1,
        ease: 'power3.out',
        delay: 0.2
    })
        .from('.display-text .word span', {
            y: 100,
            opacity: 0,
            duration: 1.5,
            stagger: 0.1,
            ease: 'power4.out',
            skewY: 7
        }, '-=0.8')
        .from('.hero-cta', {
            y: 20,
            opacity: 0,
            duration: 1,
            ease: 'power3.out'
        }, '-=1');

    // Parallax Orb
    gsap.to('.hero-orb', {
        scrollTrigger: {
            trigger: '.hero-section',
            start: 'top top',
            end: 'bottom top',
            scrub: 1
        },
        y: 300,
        scale: 1.5
    });
}

function initMagneticButtons() {
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left - rect.width / 2;
            const y = e.clientY - rect.top - rect.height / 2;
            gsap.to(btn, { x: x * 0.3, y: y * 0.3, duration: 0.3, ease: 'power2.out' });
        });
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, { x: 0, y: 0, duration: 0.5, ease: 'elastic.out(1, 0.3)' });
        });
    });
}

function initScrollAnimations() {
    gsap.utils.toArray('.feature-card').forEach((card, i) => {
        gsap.from(card, {
            scrollTrigger: {
                trigger: card,
                start: 'top 85%',
                toggleActions: 'play none none reverse'
            },
            y: 50,
            opacity: 0,
            duration: 1,
            delay: i * 0.1,
            ease: 'power3.out'
        });
    });
}

// --- APP LOGIC ---
const pages = {
    landing: document.getElementById('landingPage'),
    register: document.getElementById('registerPage'),
    login: document.getElementById('loginPage'),
    dashboard: document.getElementById('dashboardPage')
};

function navigateTo(pageId) {
    // Transition out
    gsap.to(document.body, {
        opacity: 0, duration: 0.3, onComplete: () => {
            // Hide all
            Object.values(pages).forEach(el => el && el.classList.add('hidden'));

            // Show target
            const target = pages[pageId];
            if (target) {
                target.classList.remove('hidden');
                window.scrollTo(0, 0);

                // Handle dashboard mode - hide/show main header
                if (pageId === 'dashboard') {
                    document.body.classList.add('dashboard-mode');
                } else {
                    document.body.classList.remove('dashboard-mode');
                }

                // Re-init animations based on page
                if (pageId === 'landing') {
                    setTimeout(() => {
                        initHeroAnimations();
                        initScrollAnimations();
                        initRevealAnimations();
                        initMagneticButtons();
                    }, 100);
                } else {
                    initMagneticButtons();
                }
            }

            // Transition in
            gsap.to(document.body, { opacity: 1, duration: 0.5 });
        }
    });
}

function initRevealAnimations() {
    const reveals = document.querySelectorAll('[data-reveal]');
    reveals.forEach(el => {
        gsap.fromTo(el,
            { y: 50, opacity: 0 },
            {
                scrollTrigger: {
                    trigger: el,
                    start: 'top 85%',
                    toggleActions: 'play none none reverse'
                },
                y: 0,
                opacity: 1,
                duration: 1,
                ease: 'power3.out'
            }
        );
    });
}

// --- AUTH ---
async function handleRegister(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
        const res = await fetch(`${BASE_URL}/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        // Parse the response to get the message
        const result = await res.json();

        if (res.ok) {
            showToast('success', 'Account Created!', 'Welcome to Aura. Please login to continue.');
            navigateTo('login');
        } else {
            // Show the actual error from Python ("Username already taken")
            showToast('error', 'Registration Failed', result.error || 'Please check your details and try again.');
        }
    } catch (err) { 
        console.error(err);
        showToast('error', 'Connection Error', 'Unable to connect to server. Please try again.');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(e.target));
    try {
        const res = await fetch(`${BASE_URL}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        if (res.ok) {
            currentUserId = result.user_id;
            // Save to localStorage for persistent login
            localStorage.setItem('aura_user_id', result.user_id);
            localStorage.setItem('aura_user_name', result.name || 'User');
            showToast('success', 'Login Successful', `Welcome back, ${result.name || 'User'}!`);
            loadDashboardData();
            navigateTo('dashboard');
        } else {
            showToast('error', 'Access Denied', result.error || 'Invalid username or password.');
        }
    } catch (err) { 
        console.error(err);
        showToast('error', 'Connection Error', 'Unable to connect to server. Please try again.');
    }
}

// --- DASHBOARD ---
async function loadDashboardData() {
    if (!currentUserId) return;

    // Show loading state
    showDashboardLoading(true);

    // Initialize empty chart immediately to show structure
    renderChart([]);

    try {
        const res = await fetch(`${BASE_URL}/api/dashboard?user_id=${currentUserId}`);
        const data = await res.json();
        if (res.ok) {
            showDashboardLoading(false);
            updateDashboardUI(data);
        }
    } catch (err) { 
        console.error(err);
        showDashboardLoading(false);
    }
}

// Show/hide dashboard loading state
function showDashboardLoading(isLoading) {
    const dashboard = document.getElementById('dashboard');
    const greetingText = document.getElementById('greeting-text');
    const dateText = document.getElementById('current-date');
    
    if (isLoading) {
        dashboard?.classList.add('dashboard-loading');
        if (greetingText) greetingText.innerText = 'Loading...';
        if (dateText) dateText.innerText = 'Please wait';
    } else {
        dashboard?.classList.remove('dashboard-loading');
    }
}

function updateDashboardUI(data) {
    const latest = data.glucose_readings.at(-1)?.glucose_value || 0;
    const healthScore = data.health_score || {};
    const score = healthScore.score ?? calculateScoreFromReadings(data.glucose_readings);
    const userName = data.user_profile?.name || 'User';
    const readings = data.glucose_readings || [];

    // Update current date with time (AM/PM)
    const now = new Date();
    const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' });
    const timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
    document.getElementById('current-date').innerText = `${dateStr} • ${timeStr}`;

    // Determine time of day for greeting
    const hour = now.getHours();
    let timeOfDay = 'evening';
    if (hour < 12) timeOfDay = 'morning';
    else if (hour < 18) timeOfDay = 'afternoon';

    // Update Greeting
    document.getElementById('greeting-text').innerText = `Good ${timeOfDay}, ${userName}!`;

    // Update Health Score with circular progress (Bottom Card)
    updateCircularProgress(score);
    gsap.to('#score-number-bottom', {
        innerText: score,
        duration: 2,
        snap: { innerText: 1 },
        ease: 'power2.out'
    });

    // Set score status
    let status = 'Needs attention';
    if (score >= 80) status = 'Excellent';
    else if (score >= 60) status = 'Good';
    else if (score >= 40) status = 'Fair';
    document.getElementById('score-status-bottom').innerText = status;

    // Update Time in Range - use API value first, then calculate
    const timeInRange = healthScore.time_in_range_percent ?? calculateTimeInRange(readings);
    const timeInRangeEl = document.getElementById('time-in-range');
    if (timeInRangeEl) timeInRangeEl.innerText = `${Math.round(timeInRange)}%`;

    // Update Range Bar
    const rangeBar = document.getElementById('range-bar-bottom');
    if (rangeBar) {
        rangeBar.style.width = `${timeInRange}%`;
        // Color based on value
        if (timeInRange >= 70) rangeBar.style.background = '#4ade80'; // Green
        else if (timeInRange >= 50) rangeBar.style.background = '#fbbf24'; // Yellow
        else rangeBar.style.background = '#f87171'; // Red
    }

    // Render chart
    renderChart(readings);

    // Only animate cards on first load, not on updates
    if (!window.dashboardAnimated) {
        window.dashboardAnimated = true;
        gsap.fromTo('.dashboard-card', 
            { opacity: 0, y: 20 },
            { opacity: 1, y: 0, duration: 0.6, stagger: 0.1, ease: 'power2.out' }
        );
    }
}

function calculateTrend(readings) {
    if (readings.length < 2) return { text: 'Stable', icon: '→', slope: 0 };
    const recent = readings.slice(-5);
    const values = recent.map(r => r.glucose_value);
    const avg1 = values.slice(0, 2).reduce((a, b) => a + b, 0) / 2;
    const avg2 = values.slice(-2).reduce((a, b) => a + b, 0) / 2;
    const slope = avg2 - avg1;

    if (slope > 5) return { text: 'Rising', icon: '↗', slope };
    if (slope < -5) return { text: 'Falling', icon: '↘', slope };
    return { text: 'Stable', icon: '→', slope };
}

function calculateTimeInRange(readings) {
    if (!readings || readings.length === 0) return 0;
    const inRange = readings.filter(r => r.glucose_value >= 70 && r.glucose_value <= 180).length;
    return Math.round((inRange / readings.length) * 100);
}

// Fallback: Calculate health score from readings on frontend
function calculateScoreFromReadings(readings) {
    if (!readings || readings.length < 3) return 0;
    
    const values = readings.map(r => r.glucose_value);
    let score = 100;
    
    // Time in range penalty
    const inRange = values.filter(v => v >= 70 && v <= 180).length;
    const timeInRangePercent = (inRange / values.length) * 100;
    score -= (100 - timeInRangePercent) * 0.5;
    
    // Hypo penalty
    const hypoEvents = values.filter(v => v < 70).length;
    score -= hypoEvents * 5;
    
    // Very high penalty
    const veryHighEvents = values.filter(v => v > 250).length;
    score -= veryHighEvents * 2;
    
    return Math.max(0, Math.min(100, Math.round(score)));
}

function updateCircularProgress(score) {
    const circle = document.getElementById('score-circle-bottom');
    if (!circle) return;

    const circumference = 2 * Math.PI * 45; // 2πr where r=45 (new size)
    const offset = circumference - (score / 100) * circumference;

    gsap.to(circle, {
        strokeDashoffset: offset,
        duration: 2,
        ease: 'power2.out'
    });
}

function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('main').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.dashboard-layout').forEach(el => el.classList.add('hidden')); // Hide dashboard too

    const target = document.getElementById(sectionId);
    if (target) target.classList.remove('hidden');

    // Handle dashboard mode class on body
    if (sectionId === 'dashboardPage') {
        document.body.classList.add('dashboard-mode');
    } else {
        document.body.classList.remove('dashboard-mode');
    }
}

// SIDEBAR NAVIGATION
document.getElementById('nav-dashboard').addEventListener('click', (e) => {
    e.preventDefault();
    showDashboardSection('dashboard');
});

document.getElementById('nav-analytics').addEventListener('click', (e) => {
    e.preventDefault();
    showDashboardSection('analytics');
    loadAnalyticsData();
});

document.getElementById('nav-settings').addEventListener('click', (e) => {
    e.preventDefault();
    showDashboardSection('settings');
    loadSettingsData();
});

document.getElementById('nav-logout').addEventListener('click', (e) => {
    e.preventDefault();
    handleLogout();
});

// Show different sections within dashboard
function showDashboardSection(section) {
    const dashboardContainer = document.getElementById('dashboardContainer');
    const analyticsContainer = document.getElementById('analyticsContainer');
    const settingsContainer = document.getElementById('settingsContainer');
    
    // Safety check
    if (!dashboardContainer || !analyticsContainer || !settingsContainer) {
        console.error('Dashboard containers not found');
        return;
    }
    
    // Update nav active states
    document.querySelectorAll('.sidebar-link').forEach(item => item.classList.remove('active'));
    
    // Hide all containers first (add hidden class)
    dashboardContainer.classList.add('hidden');
    analyticsContainer.classList.add('hidden');
    settingsContainer.classList.add('hidden');
    
    if (section === 'dashboard') {
        dashboardContainer.classList.remove('hidden');
        document.getElementById('nav-dashboard').classList.add('active');
    } else if (section === 'analytics') {
        analyticsContainer.classList.remove('hidden');
        document.getElementById('nav-analytics').classList.add('active');
    } else if (section === 'settings') {
        settingsContainer.classList.remove('hidden');
        document.getElementById('nav-settings').classList.add('active');
    }
}

// Load analytics data
function loadAnalyticsData() {
    const userId = localStorage.getItem('aura_user_id') || localStorage.getItem('user_id');
    if (!userId) return;
    
    // Fetch glucose readings for analytics
    fetch(`${BASE_URL}/api/dashboard?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.glucose_readings && data.glucose_readings.length > 0) {
                updateAnalyticsStats(data.glucose_readings);
                updateDistributionChart(data.glucose_readings);
            }
        })
        .catch(err => console.error('Error loading analytics:', err));
    
    // Load meal and activity logs
    loadMealLogs();
    loadActivityLogs();
}

function updateAnalyticsStats(readings) {
    // Calculate average glucose
    const values = readings.map(r => r.glucose_value);
    const avg = Math.round(values.reduce((a, b) => a + b, 0) / values.length);
    
    // Count readings
    const count = readings.length;
    
    // Time in range (70-180 mg/dL)
    const inRange = values.filter(v => v >= 70 && v <= 180).length;
    const timeInRange = Math.round((inRange / values.length) * 100);
    
    // Hypo events (below 70)
    const hypoEvents = values.filter(v => v < 70).length;
    
    // Update DOM - use correct IDs from HTML
    document.getElementById('avg-glucose').textContent = avg;
    document.getElementById('readings-count').textContent = count;
    document.getElementById('time-in-range-analytics').textContent = timeInRange + '%';
    document.getElementById('hypo-count').textContent = hypoEvents;
}

function updateDistributionChart(readings) {
    const values = readings.map(r => r.glucose_value);
    const total = values.length;
    
    const low = values.filter(v => v < 70).length;
    const normal = values.filter(v => v >= 70 && v <= 180).length;
    const high = values.filter(v => v > 180).length;
    
    const lowPct = Math.round((low / total) * 100);
    const normalPct = Math.round((normal / total) * 100);
    const highPct = Math.round((high / total) * 100);
    
    // Update distribution bars - use correct IDs from HTML
    document.getElementById('dist-low').style.width = lowPct + '%';
    document.getElementById('dist-low-pct').textContent = lowPct + '%';
    
    document.getElementById('dist-range').style.width = normalPct + '%';
    document.getElementById('dist-range-pct').textContent = normalPct + '%';
    
    document.getElementById('dist-high').style.width = highPct + '%';
    document.getElementById('dist-high-pct').textContent = highPct + '%';
}

function loadMealLogs() {
    // For now, show placeholder data - this would come from API
    const mealList = document.getElementById('meal-logs');
    if (mealList) {
        mealList.innerHTML = `
            <div class="log-item">
                <div class="icon">🍛</div>
                <div class="details">
                    <div class="name">Lunch - Rice & Dal</div>
                    <div class="meta">~450 cal • 65g carbs</div>
                </div>
                <div class="time">12:30 PM</div>
            </div>
            <div class="log-item">
                <div class="icon">🥣</div>
                <div class="details">
                    <div class="name">Breakfast - Oats</div>
                    <div class="meta">~280 cal • 45g carbs</div>
                </div>
                <div class="time">8:00 AM</div>
            </div>
            <p style="text-align: center; color: var(--text-tertiary); font-size: 0.85rem; margin-top: 12px;">
                Log meals via chat to see them here
            </p>
        `;
    }
}

function loadActivityLogs() {
    // For now, show placeholder data - this would come from API
    const activityList = document.getElementById('activity-logs');
    if (activityList) {
        activityList.innerHTML = `
            <div class="log-item activity">
                <div class="icon">🚶</div>
                <div class="details">
                    <div class="name">Morning Walk</div>
                    <div class="meta">30 min • ~150 cal burned</div>
                </div>
                <div class="time">7:00 AM</div>
            </div>
            <p style="text-align: center; color: var(--text-tertiary); font-size: 0.85rem; margin-top: 12px;">
                Log activities via chat to see them here
            </p>
        `;
    }
}

// Load settings data
function loadSettingsData() {
    const userId = localStorage.getItem('aura_user_id') || localStorage.getItem('user_id');
    const userName = localStorage.getItem('aura_user_name');
    
    // Pre-fill known data
    if (userName) {
        const nameInput = document.getElementById('settingsName');
        if (nameInput) nameInput.value = userName;
    }
    
    // Load saved settings from localStorage
    const settings = JSON.parse(localStorage.getItem('aura_settings') || '{}');
    
    if (settings.email) document.getElementById('settingsEmail').value = settings.email;
    if (settings.age) document.getElementById('settingsAge').value = settings.age;
    if (settings.diabetesType) document.getElementById('diabetesType').value = settings.diabetesType;
    if (settings.targetLow) document.getElementById('targetLow').value = settings.targetLow;
    if (settings.targetHigh) document.getElementById('targetHigh').value = settings.targetHigh;
    if (settings.fastActingInsulin) document.getElementById('fastActingInsulin').value = settings.fastActingInsulin;
    if (settings.longActingInsulin) document.getElementById('longActingInsulin').value = settings.longActingInsulin;
    if (settings.carbRatio) document.getElementById('carbRatio').value = settings.carbRatio;
}

// Save profile settings
function saveProfileSettings() {
    const settings = JSON.parse(localStorage.getItem('aura_settings') || '{}');
    
    settings.name = document.getElementById('settingsName').value;
    settings.email = document.getElementById('settingsEmail').value;
    settings.age = document.getElementById('settingsAge').value;
    settings.diabetesType = document.getElementById('diabetesType').value;
    
    localStorage.setItem('aura_settings', JSON.stringify(settings));
    
    // Update display name if changed
    if (settings.name) {
        localStorage.setItem('aura_user_name', settings.name);
        const nameDisplay = document.querySelector('.user-name');
        if (nameDisplay) nameDisplay.textContent = settings.name;
    }
    
    showToast('Profile saved successfully!', 'success');
}

// Save glucose targets
function saveGlucoseTargets() {
    const settings = JSON.parse(localStorage.getItem('aura_settings') || '{}');
    
    settings.targetLow = document.getElementById('targetLow').value;
    settings.targetHigh = document.getElementById('targetHigh').value;
    
    localStorage.setItem('aura_settings', JSON.stringify(settings));
    showToast('Glucose targets updated!', 'success');
}

// Save insulin settings
function saveInsulinSettings() {
    const settings = JSON.parse(localStorage.getItem('aura_settings') || '{}');
    
    settings.fastActingInsulin = document.getElementById('fastActingInsulin').value;
    settings.longActingInsulin = document.getElementById('longActingInsulin').value;
    settings.carbRatio = document.getElementById('carbRatio').value;
    
    localStorage.setItem('aura_settings', JSON.stringify(settings));
    showToast('Insulin settings saved!', 'success');
}

// Data management functions
function exportData() {
    const userId = localStorage.getItem('aura_user_id') || localStorage.getItem('user_id');
    if (!userId) {
        showToast('Please log in first', 'warning');
        return;
    }
    
    // Fetch all user data and create downloadable file
    fetch(`${BASE_URL}/api/dashboard?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            const exportData = {
                user_id: userId,
                exported_at: new Date().toISOString(),
                readings: data.readings || [],
                settings: JSON.parse(localStorage.getItem('aura_settings') || '{}')
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `aura_data_${userId}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showToast('Data exported successfully!', 'success');
        })
        .catch(err => {
            console.error('Export error:', err);
            showToast('Failed to export data', 'error');
        });
}

function clearAllData() {
    if (confirm('Are you sure you want to delete all your data? This action cannot be undone.')) {
        localStorage.removeItem('aura_settings');
        localStorage.removeItem('aura_user_id');
        localStorage.removeItem('aura_user_name');
        localStorage.removeItem('token');
        localStorage.removeItem('user_id');
        
        showToast('All data cleared', 'info');
        
        setTimeout(() => {
            showSection('landingPage');
        }, 1500);
    }
}

function renderChart(readings, predictedValues = null) {
    const canvas = document.getElementById('glucoseChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');

    // Destroy existing chart if it exists
    if (window.glucoseChartInstance) {
        window.glucoseChartInstance.destroy();
    }

    // Prepare data arrays
    let labels = [];
    let historicalData = [];
    let predictedData = [];
    
    const now = new Date();
    
    if (!readings || readings.length === 0) {
        // Show placeholder with time labels
        for (let i = 6; i >= 0; i--) {
            const time = new Date(now - i * 60 * 60000);
            labels.push(formatTimeLabel(time));
            historicalData.push(null);
        }
        // Future predictions
        for (let i = 1; i <= 2; i++) {
            const time = new Date(now.getTime() + i * 60 * 60000);
            labels.push(formatTimeLabel(time));
            predictedData.push(null);
        }
    } else {
        // Sample readings to show max ~12 points for readability
        const sampledReadings = sampleReadings(readings, 12);
        
        sampledReadings.forEach(r => {
            const d = new Date(r.timestamp);
            labels.push(formatTimeLabel(d));
            historicalData.push(r.glucose_value);
        });
        
        // Add predicted values
        const lastReading = sampledReadings[sampledReadings.length - 1]?.glucose_value || 100;
        const trend = calculateTrend(sampledReadings);
        
        // Bridge connection point
        predictedData = new Array(sampledReadings.length - 1).fill(null);
        predictedData.push(lastReading);
        
        // Add 2 future prediction points (1hr and 2hr)
        for (let i = 1; i <= 2; i++) {
            const time = new Date(now.getTime() + i * 60 * 60000);
            labels.push(formatTimeLabel(time));
            historicalData.push(null);
            
            const predicted = predictedValues && predictedValues[i-1] 
                ? predictedValues[i-1] 
                : Math.round(lastReading + (trend.slope * i * 2));
            predictedData.push(Math.max(50, Math.min(350, predicted)));
        }
    }

    // Calculate dynamic Y-axis range based on data
    const allValues = [...historicalData, ...predictedData].filter(v => v !== null);
    const minVal = allValues.length > 0 ? Math.min(...allValues, 70) : 70;
    const maxVal = allValues.length > 0 ? Math.max(...allValues, 180) : 180;
    const yMin = Math.max(40, Math.floor((minVal - 30) / 20) * 20);
    const yMax = Math.min(400, Math.ceil((maxVal + 30) / 20) * 20);

    window.glucoseChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                // Target range upper bound (180) - dashed line
                {
                    label: 'High Threshold',
                    data: labels.map(() => 180),
                    borderColor: 'rgba(251, 191, 36, 0.5)',
                    borderWidth: 2,
                    borderDash: [6, 4],
                    pointRadius: 0,
                    fill: false,
                    order: 4
                },
                // Target range lower bound (70) - dashed line with fill
                {
                    label: 'Low Threshold',
                    data: labels.map(() => 70),
                    borderColor: 'rgba(251, 191, 36, 0.5)',
                    borderWidth: 2,
                    borderDash: [6, 4],
                    pointRadius: 0,
                    fill: '-1',
                    backgroundColor: 'rgba(74, 222, 128, 0.06)',
                    order: 4
                },
                // Historical glucose - main line
                {
                    label: 'Historical',
                    data: historicalData,
                    borderColor: '#a855f7',
                    backgroundColor: (context) => {
                        const chart = context.chart;
                        const {ctx, chartArea} = chart;
                        if (!chartArea) return 'rgba(168, 85, 247, 0.15)';
                        const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                        gradient.addColorStop(0, 'rgba(168, 85, 247, 0.25)');
                        gradient.addColorStop(0.6, 'rgba(168, 85, 247, 0.08)');
                        gradient.addColorStop(1, 'rgba(168, 85, 247, 0)');
                        return gradient;
                    },
                    borderWidth: 3,
                    pointBackgroundColor: (context) => {
                        const value = context.raw;
                        if (value === null) return 'transparent';
                        if (value < 70) return '#ef4444';
                        if (value > 180) return '#f59e0b';
                        return '#a855f7';
                    },
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    fill: true,
                    tension: 0.3,
                    order: 1,
                    spanGaps: false
                },
                // Predicted glucose - dashed line
                {
                    label: 'Predicted',
                    data: predictedData,
                    borderColor: '#22d3ee',
                    backgroundColor: 'rgba(34, 211, 238, 0.08)',
                    borderWidth: 3,
                    borderDash: [10, 6],
                    pointBackgroundColor: '#22d3ee',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 9,
                    fill: true,
                    tension: 0.3,
                    order: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { top: 15, right: 20, bottom: 10, left: 10 }
            },
            plugins: {
                legend: { 
                    display: false // Using custom HTML legend
                },
                tooltip: {
                    enabled: true,
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(10, 10, 15, 0.95)',
                    titleColor: '#fff',
                    titleFont: { size: 13, weight: '600' },
                    bodyColor: 'rgba(255,255,255,0.85)',
                    bodyFont: { size: 12 },
                    borderColor: 'rgba(168, 85, 247, 0.4)',
                    borderWidth: 1,
                    padding: 14,
                    cornerRadius: 10,
                    displayColors: true,
                    boxPadding: 6,
                    callbacks: {
                        title: function(items) {
                            return `⏰ ${items[0].label}`;
                        },
                        label: function(context) {
                            if (context.dataset.label === 'High Threshold' || context.dataset.label === 'Low Threshold') {
                                return null;
                            }
                            if (context.raw === null) return null;
                            const value = context.raw;
                            let status = '✅ Normal';
                            if (value < 70) status = '⚠️ Low';
                            else if (value > 180) status = '⚠️ High';
                            return `${context.dataset.label}: ${Math.round(value)} mg/dL ${status}`;
                        },
                        labelColor: function(context) {
                            return {
                                borderColor: context.dataset.borderColor,
                                backgroundColor: context.dataset.borderColor,
                                borderRadius: 4
                            };
                        }
                    }
                }
            },
            scales: {
                y: {
                    min: yMin,
                    max: yMax,
                    grid: { 
                        color: 'rgba(255, 255, 255, 0.04)',
                        drawBorder: false
                    },
                    border: { display: false },
                    ticks: { 
                        color: 'rgba(255, 255, 255, 0.5)',
                        font: { size: 11, weight: '500' },
                        padding: 12,
                        stepSize: Math.ceil((yMax - yMin) / 5 / 10) * 10,
                        callback: function(value) {
                            return value + ' mg/dL';
                        }
                    }
                },
                x: {
                    grid: { display: false },
                    border: { display: false },
                    ticks: { 
                        color: 'rgba(255, 255, 255, 0.5)',
                        font: { size: 10, weight: '500' },
                        padding: 10,
                        maxRotation: 0,
                        autoSkip: true,
                        maxTicksLimit: 8
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

// Helper: Format time for chart labels (12-hour format with AM/PM)
function formatTimeLabel(date) {
    const hours = date.getHours();
    const mins = date.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    const h = hours % 12 || 12;
    if (mins === 0) return `${h} ${ampm}`;
    return `${h}:${mins.toString().padStart(2, '0')} ${ampm}`;
}

// Helper: Sample readings to reduce clutter on chart
function sampleReadings(readings, maxPoints) {
    if (readings.length <= maxPoints) return readings;
    const step = Math.ceil(readings.length / maxPoints);
    const sampled = [];
    for (let i = 0; i < readings.length; i += step) {
        sampled.push(readings[i]);
    }
    // Always include the last reading for accuracy
    if (sampled[sampled.length - 1] !== readings[readings.length - 1]) {
        sampled.push(readings[readings.length - 1]);
    }
    return sampled;
}

// --- CHAT ---
async function handleChat() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // Add user message
    addChatMessage(message, 'user');
    input.value = '';

    // Add thinking indicator
    const thinkingId = addThinkingIndicator();

    try {
        const res = await fetch(`${BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, user_id: currentUserId })
        });
        const data = await res.json();

        // Remove thinking indicator
        removeThinkingIndicator(thinkingId);

        // Build a conversational, helpful response
        let responseText = '';
        const intent = data.parsed_info?.intent || 'unknown';
        const lastGlucose = data.glucose_prediction?.last_known_glucose || 120;

        // Check if user logged food
        if (data.parsed_info && data.parsed_info.foods_detected && data.parsed_info.foods_detected.length > 0) {
            const foods = data.parsed_info.foods_detected;
            const totalCarbs = data.parsed_info.carbs || 0;

            responseText += `✅ **Logged Successfully!**\n\n`;
            
            // Display each food with quantity and carbs
            responseText += `🍽️ **Foods detected:**\n`;
            foods.forEach(f => {
                const qty = f.quantity > 1 ? `${f.quantity}x ` : '';
                const carbInfo = f.carbs ? ` (${f.carbs}g carbs)` : '';
                responseText += `• ${qty}${f.food}${carbInfo}\n`;
            });
            responseText += `\n`;

            if (totalCarbs > 0) {
                responseText += `📊 **Total carbs: ${totalCarbs}g**\n\n`;
                
                // Carb impact assessment
                if (totalCarbs > 60) {
                    responseText += `⚠️ This is a high-carb meal. Monitor your glucose closely over the next 2 hours.\n\n`;
                } else if (totalCarbs > 30) {
                    responseText += `📝 Moderate carb intake. Good balance!\n\n`;
                } else {
                    responseText += `✨ Low-carb choice! This should have minimal glucose impact.\n\n`;
                }
            }

            // Add insulin recommendation if available
            if (data.dose_recommendation && data.dose_recommendation.recommended_dose > 0) {
                responseText += `💉 **Insulin Recommendation:**\n`;
                responseText += `• Suggested dose: **${data.dose_recommendation.recommended_dose} units**\n`;
                if (data.dose_recommendation.reasoning) {
                    responseText += `• ${data.dose_recommendation.reasoning}\n`;
                }
                responseText += `\n`;

                if (data.contextual_advice?.timing_considerations?.length > 0) {
                    responseText += `⏰ **Timing tip:** ${data.contextual_advice.timing_considerations[0]}\n\n`;
                }
            }

            // Add health tips if available
            if (data.parsed_info.health_tips && data.parsed_info.health_tips.length > 0) {
                responseText += `💡 **Tips:**\n`;
                data.parsed_info.health_tips.forEach(tip => {
                    responseText += `• ${tip}\n`;
                });
                responseText += `\n`;
            }

            // Add activity suggestion based on current glucose
            if (lastGlucose > 140 && totalCarbs > 30) {
                responseText += `🏃 **Activity suggestion:** A 15-20 min walk after eating can help manage post-meal glucose spikes.\n`;
            }
        }
        // If user logged activity
        else if (data.parsed_info?.activities_detected && data.parsed_info.activities_detected.length > 0) {
            const activities = data.parsed_info.activities_detected;
            
            responseText += `🏃 **Activity Logged!**\n\n`;
            activities.forEach(a => {
                const duration = a.duration ? ` for ${a.duration} mins` : '';
                responseText += `• ${a.activity}${duration}\n`;
                if (a.glucose_impact) {
                    const impact = a.glucose_impact;
                    if (impact === 'high_reduction') {
                        responseText += `  → Expected: Significant glucose reduction\n`;
                    } else if (impact === 'moderate_reduction') {
                        responseText += `  → Expected: Moderate glucose reduction\n`;
                    } else {
                        responseText += `  → Expected: Mild glucose reduction\n`;
                    }
                }
            });
            responseText += `\n`;

            // Add safety tips
            if (lastGlucose < 100) {
                responseText += `⚠️ **Caution:** Your glucose is ${lastGlucose} mg/dL. Consider having a small snack before exercise to prevent lows.\n\n`;
            } else {
                responseText += `✅ Great job staying active! Exercise helps improve insulin sensitivity.\n\n`;
            }

            // Add health tips if available
            if (data.parsed_info.health_tips && data.parsed_info.health_tips.length > 0) {
                responseText += `💡 **Tips:**\n`;
                data.parsed_info.health_tips.slice(0, 2).forEach(tip => {
                    responseText += `• ${tip}\n`;
                });
            }
        }
        // If asking about glucose status or trends
        else if (data.glucose_prediction && data.glucose_prediction.analysis) {
            const trend = data.glucose_prediction.analysis.trend;
            const slope = data.glucose_prediction.analysis.slope;

            // Determine emoji based on trend
            const trendEmoji = trend === 'rising' ? '📈' : trend === 'falling' ? '📉' : '➡️';
            const trendText = trend === 'rising' ? 'rising' : trend === 'falling' ? 'falling' : 'stable';

            responseText += `${trendEmoji} **Your Glucose Status**\n\n`;
            responseText += `• Latest reading: **${lastGlucose} mg/dL**\n`;
            responseText += `• Trend: ${trendText} (${slope > 0 ? '+' : ''}${slope.toFixed(2)} mg/dL per reading)\n\n`;

            // Status indicator with color guide
            let statusEmoji, statusText, statusAdvice;
            if (lastGlucose < 70) {
                statusEmoji = '🔴';
                statusText = 'LOW';
                statusAdvice = 'Have 15-20g of fast-acting carbs (juice, glucose tabs, candy).';
            } else if (lastGlucose < 80) {
                statusEmoji = '🟠';
                statusText = 'SLIGHTLY LOW';
                statusAdvice = 'Consider a small snack if you\'re active or have insulin on board.';
            } else if (lastGlucose <= 140) {
                statusEmoji = '🟢';
                statusText = 'IN RANGE';
                statusAdvice = 'Excellent! Keep up the good work.';
            } else if (lastGlucose <= 180) {
                statusEmoji = '🟡';
                statusText = 'SLIGHTLY HIGH';
                statusAdvice = 'Monitor closely. Light activity can help.';
            } else {
                statusEmoji = '🔴';
                statusText = 'HIGH';
                statusAdvice = 'Stay hydrated. Check if correction is needed.';
            }

            responseText += `${statusEmoji} **Status: ${statusText}**\n`;
            responseText += `${statusAdvice}\n\n`;

            // Add prediction if available
            if (data.glucose_prediction.adjusted_prediction && data.glucose_prediction.adjusted_prediction.length > 0) {
                const pred30 = data.glucose_prediction.adjusted_prediction[2];
                const pred60 = data.glucose_prediction.adjusted_prediction[5];
                responseText += `🔮 **Predictions:**\n`;
                responseText += `• In 30 min: ~${pred30} mg/dL\n`;
                if (pred60) {
                    responseText += `• In 60 min: ~${pred60} mg/dL\n`;
                }
                responseText += `\n`;
            }

            // Smart suggestions based on glucose level
            responseText += getSuggestions(lastGlucose, trend);

            // Add health tips if available
            if (data.parsed_info?.health_tips && data.parsed_info.health_tips.length > 0) {
                responseText += `💡 **Personalized Tips:**\n`;
                data.parsed_info.health_tips.forEach(tip => {
                    responseText += `• ${tip}\n`;
                });
            }
        }
        // Handle questions
        else if (intent === 'question' || message.toLowerCase().includes('what') || 
                 message.toLowerCase().includes('how') || message.toLowerCase().includes('should')) {
            responseText = handleQuestion(message, lastGlucose, data);
        }
        // Greeting response
        else if (intent === 'greeting' || isGreeting(message)) {
            const timeOfDay = getTimeOfDay();
            const greetings = [
                `👋 Good ${timeOfDay}! I'm Aura, your AI health companion.`,
                `Hey there! 😊 Hope you're having a great ${timeOfDay}!`,
                `Hello! 🌟 Ready to help you stay healthy today.`
            ];
            responseText = greetings[Math.floor(Math.random() * greetings.length)] + `\n\n`;
            
            // Quick status if we have data
            if (lastGlucose) {
                const statusEmoji = lastGlucose < 70 ? '🔴' : lastGlucose <= 140 ? '🟢' : '🟡';
                responseText += `${statusEmoji} Your glucose is currently **${lastGlucose} mg/dL**\n\n`;
            }

            responseText += `**How can I help you today?**\n\n`;
            responseText += `📊 "How's my glucose?"\n`;
            responseText += `🍽️ "I had rice and dal"\n`;
            responseText += `🏃 "I went for a walk"\n`;
            responseText += `❓ "What should I eat?"\n`;
        }
        // Default helpful response
        else {
            responseText = `🤔 I'm not sure I understood that completely.\n\n`;
            responseText += `Here's what I can help with:\n\n`;
            responseText += `**Log Food** 🍽️\n`;
            responseText += `"I ate 2 rotis with dal"\n`;
            responseText += `"Had a sandwich and coffee"\n\n`;
            responseText += `**Log Activity** 🏃\n`;
            responseText += `"Walked for 30 minutes"\n`;
            responseText += `"Did yoga this morning"\n\n`;
            responseText += `**Check Status** 📊\n`;
            responseText += `"How's my glucose?"\n`;
            responseText += `"What's my trend?"\n\n`;
            responseText += `**Get Suggestions** 💡\n`;
            responseText += `"What should I eat?"\n`;
            responseText += `"Recommend an activity"\n`;
        }

        addChatMessage(responseText, 'ai');

        // Refresh dashboard data after any food logging or prediction
        if (data.parsed_info?.foods_detected?.length > 0 || 
            data.parsed_info?.activities_detected?.length > 0 || 
            data.glucose_prediction) {
            setTimeout(() => loadDashboardData(), 500);
        }
    } catch (err) {
        removeThinkingIndicator(thinkingId);
        console.error(err);
        addChatMessage("⚠️ I'm having trouble connecting right now. Please try again in a moment.", 'ai');
    }
}

// Helper: Check if message is a greeting
function isGreeting(message) {
    const greetings = ['hi', 'hello', 'hey', 'howdy', 'sup', 'good morning', 'good afternoon', 'good evening', 'namaste', 'hola'];
    const lowerMsg = message.toLowerCase();
    return greetings.some(g => lowerMsg.includes(g));
}

// Helper: Get time of day
function getTimeOfDay() {
    const hour = new Date().getHours();
    if (hour < 12) return 'morning';
    if (hour < 17) return 'afternoon';
    return 'evening';
}

// Helper: Generate smart suggestions based on glucose
function getSuggestions(glucose, trend) {
    let suggestions = `\n🎯 **Suggestions:**\n`;

    if (glucose < 70) {
        // Low glucose - suggest fast carbs
        suggestions += `\n**🍬 Eat Now (fast-acting carbs):**\n`;
        suggestions += `• Glucose tablets (3-4 tabs)\n`;
        suggestions += `• Juice (1/2 cup / 120ml)\n`;
        suggestions += `• Regular soda (1/2 cup)\n`;
        suggestions += `• Candy (4-5 pieces)\n`;
        suggestions += `\n⏰ Recheck in 15 minutes.\n`;
    } else if (glucose < 100) {
        // Slightly low - suggest light snack
        suggestions += `\n**🥪 Light Snack Ideas:**\n`;
        suggestions += `• Apple with peanut butter\n`;
        suggestions += `• Crackers with cheese\n`;
        suggestions += `• Small banana\n`;
        suggestions += `• Handful of nuts + dried fruit\n`;
    } else if (glucose <= 140) {
        // In range - maintain
        suggestions += `\n**✅ You're doing great!**\n`;
        suggestions += `• Continue your current routine\n`;
        suggestions += `• Stay hydrated\n`;
        if (trend === 'stable') {
            suggestions += `• Perfect stability! 🌟\n`;
        }
    } else if (glucose <= 180) {
        // Slightly high
        suggestions += `\n**🏃 Activity Suggestions:**\n`;
        suggestions += `• 15-minute brisk walk\n`;
        suggestions += `• Light stretching/yoga\n`;
        suggestions += `• Household chores\n`;
        suggestions += `\n**🥗 Low-Carb Snack Options:**\n`;
        suggestions += `• Cucumber slices\n`;
        suggestions += `• Handful of almonds\n`;
        suggestions += `• Boiled egg\n`;
    } else {
        // High glucose
        suggestions += `\n**🚶 Recommended Activities:**\n`;
        suggestions += `• 20-30 minute walk\n`;
        suggestions += `• Light cycling\n`;
        suggestions += `• Swimming\n`;
        suggestions += `\n**💧 Also:**\n`;
        suggestions += `• Drink plenty of water\n`;
        suggestions += `• Avoid carbs for now\n`;
        suggestions += `• Check ketones if >300 mg/dL\n`;
    }

    return suggestions;
}

// Helper: Handle question intents
function handleQuestion(message, glucose, data) {
    const lowerMsg = message.toLowerCase();
    let response = '';

    if (lowerMsg.includes('eat') || lowerMsg.includes('food') || lowerMsg.includes('meal') || lowerMsg.includes('hungry')) {
        response = `🍽️ **Food Suggestions Based on Your Glucose (${glucose} mg/dL):**\n\n`;

        if (glucose < 80) {
            response += `Since your glucose is on the lower side:\n\n`;
            response += `**Quick Energy:**\n`;
            response += `• Fresh fruit (banana, apple, orange)\n`;
            response += `• Juice or smoothie\n`;
            response += `• Toast with jam\n\n`;
            response += `**Balanced Meal:**\n`;
            response += `• Rice/roti with dal & vegetables\n`;
            response += `• Sandwich with protein\n`;
            response += `• Pasta with lean protein\n`;
        } else if (glucose <= 140) {
            response += `Your glucose is in a good range! Here are balanced options:\n\n`;
            response += `**Meals:**\n`;
            response += `• Grilled chicken/fish with vegetables\n`;
            response += `• Dal + brown rice + salad\n`;
            response += `• Roti + sabzi + yogurt\n`;
            response += `• Quinoa bowl with veggies\n\n`;
            response += `**Snacks:**\n`;
            response += `• Greek yogurt with nuts\n`;
            response += `• Hummus with vegetables\n`;
            response += `• Cheese with whole grain crackers\n`;
        } else {
            response += `Since your glucose is elevated, opt for low-carb options:\n\n`;
            response += `**Best Choices:**\n`;
            response += `• Grilled chicken/fish salad\n`;
            response += `• Egg white omelette with veggies\n`;
            response += `• Paneer/tofu stir-fry\n`;
            response += `• Soup (non-creamy)\n\n`;
            response += `**Avoid for now:**\n`;
            response += `• Rice, bread, roti\n`;
            response += `• Sweets and sugary drinks\n`;
            response += `• Potatoes, bananas\n`;
        }
    } else if (lowerMsg.includes('exercise') || lowerMsg.includes('activity') || lowerMsg.includes('workout') || lowerMsg.includes('walk')) {
        response = `🏃 **Activity Recommendations (Glucose: ${glucose} mg/dL):**\n\n`;

        if (glucose < 100) {
            response += `⚠️ Have a small snack before exercising.\n\n`;
            response += `**Safe Activities:**\n`;
            response += `• Light yoga/stretching\n`;
            response += `• Gentle walk (10-15 min)\n`;
            response += `• Light household activities\n\n`;
            response += `💡 Keep fast-acting carbs nearby!\n`;
        } else if (glucose <= 180) {
            response += `✅ Great time to exercise!\n\n`;
            response += `**Recommended:**\n`;
            response += `• Brisk walking (20-30 min)\n`;
            response += `• Cycling\n`;
            response += `• Swimming\n`;
            response += `• Strength training\n`;
            response += `• Dance/aerobics\n`;
            response += `• Yoga\n`;
        } else {
            response += `⚠️ Consider light activity to help lower glucose:\n\n`;
            response += `**Best Options:**\n`;
            response += `• Walking (start slow)\n`;
            response += `• Light stretching\n`;
            response += `• Gentle cycling\n\n`;
            response += `💧 Stay well hydrated!\n`;
            response += `⏰ Check glucose again in 30-60 min.\n`;
        }
    } else if (lowerMsg.includes('insulin') || lowerMsg.includes('dose') || lowerMsg.includes('correction')) {
        response = `💉 **Insulin Guidance:**\n\n`;
        response += `Based on your current glucose of **${glucose} mg/dL**:\n\n`;

        if (glucose <= 140) {
            response += `✅ Your glucose is in target range.\n`;
            response += `• No correction typically needed\n`;
            response += `• Take meal-time insulin as prescribed if eating\n`;
        } else if (glucose <= 200) {
            response += `📝 Slightly elevated glucose.\n`;
            response += `• Small correction may help\n`;
            response += `• Consult your insulin:glucose ratio\n`;
            response += `• Consider activity first if no active insulin\n`;
        } else {
            response += `⚠️ Elevated glucose detected.\n`;
            response += `• Correction dose may be appropriate\n`;
            response += `• Check for ketones if >250 mg/dL\n`;
            response += `• Recheck in 2-3 hours\n`;
        }
        
        response += `\n⚠️ Always follow your healthcare provider's guidance for insulin dosing.\n`;
    } else {
        // Generic helpful response
        response = `❓ **Here's what I can help with:**\n\n`;
        response += `• "What should I eat?" - Food suggestions\n`;
        response += `• "What exercise should I do?" - Activity tips\n`;
        response += `• "How's my glucose?" - Current status\n`;
        response += `• "I ate [food]" - Log a meal\n`;
        response += `• "I did [activity]" - Log exercise\n`;
    }

    return response;
}

function addChatMessage(text, sender) {
    const container = document.getElementById('chat-messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${sender}`;

    if (sender === 'ai') {
        // AI message with avatar
        const avatar = document.createElement('div');
        avatar.className = 'chat-avatar';
        avatar.innerHTML = '<i class="ri-heart-pulse-fill"></i>';

        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';

        const p = document.createElement('p');
        p.style.whiteSpace = 'pre-line';

        // Simple markdown-like formatting
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') // Bold
            .replace(/\n/g, '<br>'); // Line breaks

        p.innerHTML = formattedText;
        bubble.appendChild(p);

        msgDiv.appendChild(avatar);
        msgDiv.appendChild(bubble);
    } else {
        // User message (no avatar, right-aligned)
        const bubble = document.createElement('div');
        bubble.className = 'chat-bubble';

        const p = document.createElement('p');
        p.innerText = text;
        bubble.appendChild(p);

        msgDiv.appendChild(bubble);
    }

    container.appendChild(msgDiv);
    
    // Scroll to bottom - use requestAnimationFrame for reliability
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            container.scrollTop = container.scrollHeight;
        });
    });

    // Smooth scroll animation
    gsap.fromTo(msgDiv,
        { opacity: 0, y: 10 },
        { opacity: 1, y: 0, duration: 0.3, ease: 'power2.out' }
    );
}

let thinkingCounter = 0;

function addThinkingIndicator() {
    const container = document.getElementById('chat-messages');
    const id = `thinking-${thinkingCounter++}`;

    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-msg ai';
    msgDiv.id = id;

    const avatar = document.createElement('div');
    avatar.className = 'chat-avatar';
    avatar.innerHTML = '<i class="ri-heart-pulse-fill"></i>';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble thinking-bubble';
    bubble.innerHTML = `
        <div class="thinking-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;

    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    container.appendChild(msgDiv);
    
    // Scroll to bottom
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            container.scrollTop = container.scrollHeight;
        });
    });

    return id;
}

function removeThinkingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        gsap.to(element, {
            opacity: 0,
            duration: 0.2,
            onComplete: () => element.remove()
        });
    }
}

// --- BUTTON LOADING HELPERS ---
function setButtonLoading(btn, isLoading, loadingText = 'Loading...') {
    if (!btn) return;
    
    if (isLoading) {
        btn.dataset.originalHtml = btn.innerHTML;
        btn.innerHTML = `<i class="ri-loader-4-line spinning"></i><span class="loading-text">${loadingText}</span>`;
        btn.disabled = true;
    } else {
        if (btn.dataset.originalHtml) {
            btn.innerHTML = btn.dataset.originalHtml;
        }
        btn.disabled = false;
    }
}

// --- BUTTON HANDLERS ---
async function handleCalibrateAI() {
    if (!currentUserId) return;

    const btn = document.getElementById('btn-calibrate');
    setButtonLoading(btn, true, 'Calibrating...');

    try {
        const res = await fetch(`${BASE_URL}/api/ai/calibrate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId })
        });
        const data = await res.json();
        
        // Show toast notification
        showToast('success', 'AI Calibration Started', 'Your personalized model is being trained. This may take a few minutes.');
        
        // Also show in chat
        addChatMessage(`🧠 **AI Calibration Started!**\n\n${data.message || 'Your personalized model is being trained. This may take a few minutes.'}`, 'ai');
    } catch (err) {
        console.error(err);
        showToast('error', 'Calibration Failed', 'Unable to start AI calibration. Please try again.');
        addChatMessage('⚠️ Failed to start AI calibration. Please try again.', 'ai');
    } finally {
        setButtonLoading(btn, false);
    }
}

async function handleSimulateData() {
    if (!currentUserId) return;

    const btn = document.getElementById('btn-demo-data');
    setButtonLoading(btn, true, 'Adding Data...');

    try {
        const res = await fetch(`${BASE_URL}/api/dev/simulate-data`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId })
        });
        const data = await res.json();
        
        // Show toast notification
        showToast('success', 'Demo Data Added', 'Sample glucose readings have been added. Dashboard refreshing...');
        
        // Also show in chat
        addChatMessage('✅ **Demo data added!**\n\nYour dashboard will refresh with sample glucose readings.', 'ai');
        
        // Refresh dashboard
        setTimeout(() => loadDashboardData(), 500);
    } catch (err) {
        console.error(err);
        showToast('error', 'Failed to Add Data', 'Unable to add demo data. Please try again.');
        addChatMessage('⚠️ Failed to add demo data. Please try again.', 'ai');
    } finally {
        setButtonLoading(btn, false);
    }
}

async function handleDownloadReport() {
    if (!currentUserId) {
        showToast('warning', 'Login Required', 'Please log in to download your health report.');
        return;
    }

    const btn = document.getElementById('btn-report');
    setButtonLoading(btn, true, 'Generating...');

    try {
        const res = await fetch(`${BASE_URL}/api/user/report`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: currentUserId })
        });
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `aura_health_report_${currentUserId}.pdf`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            showToast('success', 'Report Downloaded', 'Your health report has been saved to downloads.');
            addChatMessage('📄 **Report Downloaded!**\n\nYour health report has been saved to your downloads folder.', 'ai');
        } else {
            const errorData = await res.json().catch(() => ({}));
            showToast('error', 'Report Failed', errorData.error || 'Failed to generate report.');
            addChatMessage(`⚠️ ${errorData.error || 'Failed to generate report. Please try again.'}`, 'ai');
        }
    } catch (err) {
        console.error(err);
        showToast('error', 'Download Failed', 'Unable to download report. Please try again.');
        addChatMessage('⚠️ Failed to download report. Please try again.', 'ai');
    } finally {
        setButtonLoading(btn, false);
    }
}

// --- EVENTS ---
document.addEventListener('DOMContentLoaded', () => {
    // Navigation
    document.addEventListener('click', e => {
        if (e.target.matches('[data-nav]')) {
            e.preventDefault();
            navigateTo(e.target.dataset.nav);
        }
    });

    // Forms
    document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
    document.getElementById('loginForm')?.addEventListener('submit', handleLogin);

    // Chat
    document.getElementById('chat-send')?.addEventListener('click', handleChat);
    document.getElementById('chat-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleChat();
    });

    // Dashboard Buttons
    document.getElementById('btn-calibrate')?.addEventListener('click', handleCalibrateAI);
    document.getElementById('btn-demo-data')?.addEventListener('click', handleSimulateData);
    document.getElementById('btn-report')?.addEventListener('click', handleDownloadReport);
    
    // Logout button
    document.getElementById('nav-logout')?.addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
    });

    // Check for saved login - auto login if user was previously logged in
    if (checkSavedLogin()) {
        loadDashboardData();
        navigateTo('dashboard');
    } else {
        navigateTo('landing');
    }
});
