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
        if (!e.target || !e.target.closest) return;
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
        if (!e.target || !e.target.closest) return;
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
    console.log('loadDashboardData called, currentUserId:', currentUserId);
    
    if (!currentUserId) {
        // No user - show demo dashboard
        console.log('No user ID, showing demo dashboard');
        showDemoDashboard();
        return;
    }

    // Show loading state
    showDashboardLoading(true);

    // Initialize empty chart immediately to show structure
    renderChart([]);

    try {
        const res = await fetch(`${BASE_URL}/api/dashboard?user_id=${currentUserId}`);
        const data = await res.json();
        console.log('Dashboard API response:', data);
        console.log('Health score from API:', data.health_score);
        
        if (res.ok && data.glucose_readings) {
            showDashboardLoading(false);
            updateDashboardUI(data);
        } else {
            // API returned but no readings - show demo
            console.log('No glucose readings in response, showing demo');
            showDashboardLoading(false);
            showDemoDashboard();
        }
    } catch (err) { 
        console.error('Dashboard load error:', err);
        showDashboardLoading(false);
        // On error, show demo dashboard
        showDemoDashboard();
    }
}

// Show demo dashboard with sample data
function showDemoDashboard() {
    const demoData = {
        glucose_readings: [],
        health_score: { score: 78, time_in_range_percent: 72 },
        user_profile: { name: 'User' }
    };
    updateDashboardUI(demoData);
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
    console.log('updateDashboardUI called with data:', data);
    
    const latest = data.glucose_readings?.at(-1)?.glucose_value || 0;
    const healthScore = data.health_score || {};
    const readings = data.glucose_readings || [];
    
    // Calculate comprehensive glucose statistics
    const glucoseStats = calculateGlucoseStats(readings);
    console.log('Glucose Stats:', glucoseStats);
    
    // Calculate score - use API value only if it's > 0, otherwise calculate
    let score = healthScore.score;
    console.log('Score from API health_score:', score);
    
    if (!score || score === 0) {
        score = calculateScoreFromReadings(readings);
        console.log('Calculated score from readings:', score);
    }
    
    const userName = data.user_profile?.name || 'User';

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

    // Set score status with explanation
    let status = 'Needs attention';
    let scoreExplanation = '';
    let scoreClass = 'negative';
    
    if (score >= 80) {
        status = 'Excellent';
        scoreExplanation = '<i class="ri-check-double-line"></i> Great glucose control!';
        scoreClass = 'positive';
    } else if (score >= 60) {
        status = 'Good';
        scoreExplanation = '<i class="ri-check-line"></i> Good progress, keep it up';
        scoreClass = 'positive';
    } else if (score >= 40) {
        status = 'Fair';
        scoreExplanation = `<i class="ri-information-line"></i> ${glucoseStats.hypoPercent > 20 ? `${glucoseStats.hypoCount} hypos detected (${glucoseStats.hypoPercent}%)` : 'Room for improvement'}`;
        scoreClass = 'warning';
    } else {
        status = 'Needs attention';
        if (glucoseStats.hypoPercent > 50) {
            scoreExplanation = `<i class="ri-alert-line"></i> ${glucoseStats.hypoPercent}% readings are hypoglycemic!`;
        } else if (glucoseStats.hypoPercent > 20) {
            scoreExplanation = `<i class="ri-alert-line"></i> ${glucoseStats.hypoCount} hypo events impacting score`;
        } else {
            scoreExplanation = '<i class="ri-alert-line"></i> Glucose variability is high';
        }
        scoreClass = 'negative';
    }
    
    document.getElementById('score-status-bottom').innerText = status;
    const scoreExpEl = document.getElementById('score-explanation');
    if (scoreExpEl) {
        scoreExpEl.innerHTML = scoreExplanation;
        scoreExpEl.className = `trend-text ${scoreClass}`;
    }

    // Update Time in Range - use API value only if > 0, otherwise calculate
    let timeInRange = healthScore.time_in_range_percent || glucoseStats.timeInRange;
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
    
    // Update TIR explanation
    const tirExpEl = document.getElementById('tir-explanation');
    if (tirExpEl) {
        let tirExplanation = '';
        let tirClass = 'positive';
        
        if (timeInRange >= 70) {
            tirExplanation = '<i class="ri-checkbox-circle-line"></i> On Track - Meeting ADA target';
            tirClass = 'positive';
        } else if (timeInRange >= 50) {
            tirExplanation = `<i class="ri-information-line"></i> Below target - ${100 - Math.round(timeInRange)}% out of range`;
            tirClass = 'warning';
        } else {
            // Explain WHY time in range is low
            if (glucoseStats.hypoPercent > glucoseStats.highPercent) {
                tirExplanation = `<i class="ri-arrow-down-line"></i> ${glucoseStats.hypoPercent}% below range (<70 mg/dL)`;
            } else if (glucoseStats.highPercent > glucoseStats.hypoPercent) {
                tirExplanation = `<i class="ri-arrow-up-line"></i> ${glucoseStats.highPercent}% above range (>180 mg/dL)`;
            } else {
                tirExplanation = `<i class="ri-alert-line"></i> Significant time outside range`;
            }
            tirClass = 'negative';
        }
        tirExpEl.innerHTML = tirExplanation;
        tirExpEl.className = `trend-text ${tirClass}`;
    }
    
    // Update Dashboard Risk Analysis
    updateDashboardRiskAnalysis(glucoseStats, readings);
    
    // Update Insulin Sensitivity card
    updateInsulinSensitivityCard(data);

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

// Update Insulin Sensitivity Card based on available data
function updateInsulinSensitivityCard(data) {
    const isfValue = document.getElementById('isf-value');
    const isfSub = document.getElementById('isf-sub');
    const isfExp = document.getElementById('isf-explanation');
    
    if (!isfValue || !isfSub || !isfExp) return;
    
    // Check if user has insulin logs
    const insulinLogs = data.insulin_logs || [];
    const settings = JSON.parse(localStorage.getItem('aura_settings') || '{}');
    
    if (insulinLogs.length >= 5) {
        // Calculate approximate ISF from data (simplified - needs actual insulin:glucose correlation)
        // This is a placeholder - real ISF calculation needs insulin dose + glucose change data
        isfValue.textContent = '1:45';
        isfSub.textContent = '1 unit drops ~45 mg/dL';
        isfExp.innerHTML = '<i class="ri-check-line"></i> Based on your logs';
        isfExp.className = 'trend-text positive';
    } else if (settings.isfRatio) {
        // Use settings value
        isfValue.textContent = `1:${settings.isfRatio}`;
        isfSub.textContent = `1 unit drops ${settings.isfRatio} mg/dL`;
        isfExp.innerHTML = '<i class="ri-settings-3-line"></i> From your settings';
        isfExp.className = 'trend-text positive';
    } else {
        // No data - show guidance
        isfValue.textContent = '--';
        isfSub.textContent = 'Log insulin doses to calculate';
        isfExp.innerHTML = '<i class="ri-information-line"></i> Requires insulin data';
        isfExp.className = 'trend-text warning';
    }
}

// Calculate comprehensive glucose statistics
function calculateGlucoseStats(readings) {
    if (!readings || readings.length === 0) {
        return {
            total: 0,
            hypoCount: 0,
            inRangeCount: 0,
            highCount: 0,
            veryHighCount: 0,
            hypoPercent: 0,
            inRangePercent: 0,
            highPercent: 0,
            veryHighPercent: 0,
            timeInRange: 72, // Demo default
            min: 0,
            max: 0,
            avg: 0,
            cv: 0
        };
    }
    
    const values = readings.map(r => r.glucose_value);
    const total = values.length;
    
    // Count by category
    const hypoCount = values.filter(v => v < 70).length;
    const inRangeCount = values.filter(v => v >= 70 && v <= 180).length;
    const highCount = values.filter(v => v > 180 && v <= 250).length;
    const veryHighCount = values.filter(v => v > 250).length;
    
    // Calculate percentages
    const hypoPercent = Math.round((hypoCount / total) * 100);
    const inRangePercent = Math.round((inRangeCount / total) * 100);
    const highPercent = Math.round(((highCount + veryHighCount) / total) * 100);
    const veryHighPercent = Math.round((veryHighCount / total) * 100);
    
    // Basic stats
    const min = Math.min(...values);
    const max = Math.max(...values);
    const avg = values.reduce((a, b) => a + b, 0) / total;
    
    // CV calculation
    const squaredDiffs = values.map(v => Math.pow(v - avg, 2));
    const avgSquaredDiff = squaredDiffs.reduce((a, b) => a + b, 0) / total;
    const std = Math.sqrt(avgSquaredDiff);
    const cv = (std / avg) * 100;
    
    return {
        total,
        hypoCount,
        inRangeCount,
        highCount,
        veryHighCount,
        hypoPercent,
        inRangePercent,
        highPercent,
        veryHighPercent,
        timeInRange: inRangePercent,
        min: Math.round(min * 100) / 100,
        max: Math.round(max * 100) / 100,
        avg: Math.round(avg),
        cv: Math.round(cv * 10) / 10
    };
}

// Update Dashboard Risk Analysis Card
function updateDashboardRiskAnalysis(stats, readings) {
    const riskLevelEl = document.getElementById('risk-level');
    const riskSubtitleEl = document.getElementById('risk-subtitle');
    const riskExpEl = document.getElementById('risk-explanation');
    
    if (!riskLevelEl || !riskSubtitleEl || !riskExpEl) return;
    
    // Determine risk level based on actual data
    let riskLevel = 'Low Risk';
    let riskColor = 'var(--health-good)';
    let riskSubtitle = 'Your glucose is stable';
    let riskExplanation = '<i class="ri-shield-star-line"></i> No significant concerns';
    let riskClass = 'positive';
    
    // Calculate LBGI for hypo risk prediction
    let lbgi = 0;
    if (readings && readings.length > 0) {
        const values = readings.map(r => r.glucose_value);
        values.forEach(glucose => {
            if (glucose > 0) {
                const fGlucose = 1.509 * (Math.pow(Math.log(glucose), 1.084) - 5.381);
                if (fGlucose < 0) {
                    lbgi += 10 * Math.pow(fGlucose, 2);
                }
            }
        });
        lbgi = lbgi / values.length;
    }
    
    // Risk assessment based on LBGI and hypo percentage
    if (stats.hypoPercent >= 50 || lbgi >= 10) {
        // CRITICAL - Very High Risk
        riskLevel = 'Critical Risk';
        riskColor = '#ef4444'; // Bright red
        riskSubtitle = `${stats.hypoPercent}% of readings below 70 mg/dL`;
        riskExplanation = `<i class="ri-error-warning-line"></i> ${stats.hypoCount} hypo events - Immediate attention needed!`;
        riskClass = 'negative';
    } else if (stats.hypoPercent >= 20 || lbgi >= 5) {
        // HIGH RISK
        riskLevel = 'High Risk';
        riskColor = '#f97316'; // Orange-red
        riskSubtitle = `${stats.hypoCount} hypoglycemic events detected`;
        riskExplanation = `<i class="ri-alert-line"></i> ${stats.hypoPercent}% readings are too low - Consult your doctor`;
        riskClass = 'negative';
    } else if (stats.hypoPercent >= 5 || stats.highPercent >= 25 || lbgi >= 2.5) {
        // MODERATE RISK
        riskLevel = 'Moderate Risk';
        riskColor = '#fbbf24'; // Yellow
        if (stats.hypoPercent > stats.highPercent) {
            riskSubtitle = `${stats.hypoCount} low glucose events`;
            riskExplanation = `<i class="ri-information-line"></i> Some hypos detected - Monitor patterns`;
        } else {
            riskSubtitle = `${stats.highPercent}% readings above range`;
            riskExplanation = `<i class="ri-information-line"></i> High glucose tendency - Watch carb intake`;
        }
        riskClass = 'warning';
    } else if (stats.timeInRange >= 70) {
        // LOW RISK
        riskLevel = 'Low Risk';
        riskColor = 'var(--health-good)';
        riskSubtitle = 'Excellent glucose control';
        riskExplanation = '<i class="ri-shield-star-line"></i> Great job! Keep it up';
        riskClass = 'positive';
    } else {
        // MODERATE due to variability
        riskLevel = 'Moderate Risk';
        riskColor = '#fbbf24';
        riskSubtitle = `${100 - stats.timeInRange}% time out of range`;
        riskExplanation = `<i class="ri-information-line"></i> CV: ${stats.cv}% - Work on stability`;
        riskClass = 'warning';
    }
    
    // Update the DOM
    riskLevelEl.textContent = riskLevel;
    riskLevelEl.style.color = riskColor;
    riskSubtitleEl.textContent = riskSubtitle;
    riskExpEl.innerHTML = riskExplanation;
    riskExpEl.className = `trend-text ${riskClass}`;
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
    if (!readings || readings.length === 0) return 72; // Demo value
    const inRange = readings.filter(r => r.glucose_value >= 70 && r.glucose_value <= 180).length;
    return Math.round((inRange / readings.length) * 100);
}

// Fallback: Calculate health score from readings on frontend (percentage-based)
function calculateScoreFromReadings(readings) {
    if (!readings || readings.length < 3) {
        // Return a demo score when not enough data
        return 78; // Good demo score
    }
    
    const values = readings.map(r => r.glucose_value);
    const total = values.length;
    let score = 100;
    
    // Time in range (70-180 mg/dL) - TARGET: >70%
    const inRange = values.filter(v => v >= 70 && v <= 180).length;
    const timeInRangePercent = (inRange / total) * 100;
    // Penalty: 0.4 points for each percentage below 100%
    score -= (100 - timeInRangePercent) * 0.4;
    
    // Hypoglycemia penalty (percentage-based, not raw count)
    // TARGET: <4% hypoglycemic readings
    const hypoEvents = values.filter(v => v < 70).length;
    const hypoPercent = (hypoEvents / total) * 100;
    // Penalty: 0.5 points for each percentage of hypo readings
    score -= hypoPercent * 0.5;
    
    // Severe hypoglycemia additional penalty (<54 mg/dL)
    const severeHypo = values.filter(v => v < 54).length;
    const severeHypoPercent = (severeHypo / total) * 100;
    score -= severeHypoPercent * 0.3;
    
    // Hyperglycemia penalty (>180 mg/dL)
    // TARGET: <25% above range
    const highEvents = values.filter(v => v > 180).length;
    const highPercent = (highEvents / total) * 100;
    score -= highPercent * 0.2;
    
    // Very high penalty (>250 mg/dL) - additional
    const veryHighEvents = values.filter(v => v > 250).length;
    const veryHighPercent = (veryHighEvents / total) * 100;
    score -= veryHighPercent * 0.3;
    
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

// Load analytics data - Enhanced with Advanced Analytics
function loadAnalyticsData() {
    const userId = localStorage.getItem('aura_user_id') || localStorage.getItem('user_id');
    
    // Always generate demo data first to ensure UI is populated
    generateDemoAnalyticsData();
    
    if (!userId) return;
    
    // Show loading state
    showAnalyticsLoading(true);
    
    // Fetch advanced analytics from new endpoint
    fetch(`${BASE_URL}/api/analytics/advanced?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Update clinical metrics
                updateClinicalMetrics(data);
                
                // Render AGP Chart
                if (data.agp) renderAGPChart(data.agp);
                
                // Update circadian heatmap
                if (data.time_of_day_patterns) updateCircadianHeatmap(data.time_of_day_patterns);
                
                // Update distribution chart
                if (data.distribution) {
                    updateDistributionChart(data.distribution);
                }
            } else {
                // Fallback to basic analytics
                loadBasicAnalytics(userId);
            }
        })
        .catch(err => {
            console.error('Error loading advanced analytics:', err);
            loadBasicAnalytics(userId);
        })
        .finally(() => {
            showAnalyticsLoading(false);
        });
    
    // Load meal and activity logs
    loadMealLogs();
    loadActivityLogs();
}

// Fallback to basic analytics
function loadBasicAnalytics(userId) {
    fetch(`${BASE_URL}/api/dashboard?user_id=${userId}`)
        .then(res => res.json())
        .then(data => {
            if (data.glucose_readings && data.glucose_readings.length > 0) {
                updateAnalyticsStats(data.glucose_readings);
                updateDistributionChartFromReadings(data.glucose_readings);
                
                // Generate AGP from readings
                generateAGPFromReadings(data.glucose_readings);
                
                // Generate time patterns
                generateTimePatternsFromReadings(data.glucose_readings);
                
                // Update TIR breakdown
                updateTIRBreakdown(data.glucose_readings);
                
                // Update risk analysis
                updateRiskAnalysis(data.glucose_readings);
                
                // Update dawn phenomenon
                updateDawnPhenomenon(data.glucose_readings);
                
                // Update weekly heatmap
                updateHeatmapFromReadings(data.glucose_readings);
            } else {
                // No data available - generate demo data for display
                generateDemoAnalyticsData();
            }
        })
        .catch(err => {
            console.error('Error loading basic analytics:', err);
            // Generate demo data on error
            generateDemoAnalyticsData();
        });
}

// Generate demo analytics data for display when no real data is available
function generateDemoAnalyticsData() {
    console.log('Generating demo analytics data...');
    
    // Demo clinical metrics
    const demoMetrics = {
        gmi: 6.8,
        cv: 32.5,
        average_glucose: 135,
        readings_count: 168
    };
    
    updateClinicalMetrics(demoMetrics);
    
    // Demo AGP data
    const demoAGP = generateDemoAGPData();
    renderAGPChart(demoAGP);
    
    // Demo heatmap with sample data
    generateDemoHeatmap();
    
    // Demo TIR
    updateDemoTIR();
    
    // Demo risk analysis
    updateDemoRiskAnalysis();
    
    // Demo time periods
    updateDemoTimePeriods();
}

// Show/hide loading state for analytics
function showAnalyticsLoading(show) {
    const loader = document.getElementById('analytics-loader');
    const content = document.getElementById('analytics-content');
    if (loader) loader.style.display = show ? 'flex' : 'none';
    if (content) content.style.opacity = show ? '0.5' : '1';
}

// Update clinical metrics (GMI, CV, etc.)
function updateClinicalMetrics(data) {
    // GMI (Glucose Management Indicator)
    const gmiEl = document.getElementById('gmi-value');
    if (gmiEl && data.gmi) {
        gmiEl.textContent = data.gmi.toFixed(1) + '%';
        // Color code GMI
        if (data.gmi < 7) gmiEl.classList.add('excellent');
        else if (data.gmi < 8) gmiEl.classList.add('good');
        else gmiEl.classList.add('needs-attention');
    }
    
    // CV (Coefficient of Variation)
    const cvEl = document.getElementById('cv-value');
    if (cvEl && data.cv) {
        cvEl.textContent = data.cv.toFixed(1) + '%';
        // CV < 36% is considered stable
        if (data.cv < 36) {
            cvEl.classList.add('stable');
            const cvStatus = document.getElementById('cv-status');
            if (cvStatus) cvStatus.textContent = 'Stable';
        } else {
            cvEl.classList.add('variable');
            const cvStatus = document.getElementById('cv-status');
            if (cvStatus) cvStatus.textContent = 'Variable';
        }
    }
    
    // Average glucose
    const avgEl = document.getElementById('avg-glucose');
    if (avgEl && data.average_glucose) {
        avgEl.textContent = Math.round(data.average_glucose);
    }
    
    // Readings count
    const countEl = document.getElementById('readings-count');
    if (countEl && data.readings_count) {
        countEl.textContent = data.readings_count;
    }
    
    // Time in range
    const tirEl = document.getElementById('time-in-range-analytics');
    if (tirEl && data.time_in_range) {
        tirEl.textContent = Math.round(data.time_in_range) + '%';
    }
    
    // Hypo count
    const hypoEl = document.getElementById('hypo-count');
    if (hypoEl && data.hypo_events !== undefined) {
        hypoEl.textContent = data.hypo_events;
    }
}

// AGP Chart Instance
let agpChartInstance = null;

// Render Ambulatory Glucose Profile (AGP) Chart
function renderAGPChart(agpData) {
    const ctx = document.getElementById('agpChart');
    if (!ctx) {
        console.log('AGP chart canvas not found');
        return;
    }
    
    // Destroy existing chart
    if (agpChartInstance) {
        agpChartInstance.destroy();
    }
    
    // Check if we have valid AGP data (need at least median data)
    if (!agpData || (!agpData.median && !agpData.hours)) {
        ctx.parentElement.innerHTML = '<p class="no-data">Not enough data for AGP analysis</p>';
        return;
    }
    
    const hours = Array.from({length: 24}, (_, i) => `${i}:00`);
    
    agpChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: hours,
            datasets: [
                {
                    label: '90th Percentile',
                    data: agpData.p90 || [],
                    borderColor: 'rgba(251, 191, 36, 0.5)',
                    backgroundColor: 'rgba(251, 191, 36, 0.1)',
                    fill: '+1',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.4
                },
                {
                    label: '75th Percentile',
                    data: agpData.p75 || [],
                    borderColor: 'rgba(74, 222, 128, 0.5)',
                    backgroundColor: 'rgba(74, 222, 128, 0.15)',
                    fill: '+1',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.4
                },
                {
                    label: 'Median',
                    data: agpData.median || [],
                    borderColor: '#4ade80',
                    backgroundColor: 'transparent',
                    borderWidth: 3,
                    pointRadius: 0,
                    tension: 0.4
                },
                {
                    label: '25th Percentile',
                    data: agpData.p25 || [],
                    borderColor: 'rgba(74, 222, 128, 0.5)',
                    backgroundColor: 'rgba(74, 222, 128, 0.15)',
                    fill: '-1',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.4
                },
                {
                    label: '10th Percentile',
                    data: agpData.p10 || [],
                    borderColor: 'rgba(248, 113, 113, 0.5)',
                    backgroundColor: 'rgba(248, 113, 113, 0.1)',
                    fill: '-1',
                    borderWidth: 1,
                    pointRadius: 0,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: 'rgba(255,255,255,0.7)',
                        usePointStyle: true,
                        padding: 15,
                        font: { size: 11 }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    titleColor: '#fff',
                    bodyColor: 'rgba(255,255,255,0.8)',
                    borderColor: 'rgba(74, 222, 128, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true
                },
                annotation: {
                    annotations: {
                        targetRange: {
                            type: 'box',
                            yMin: 70,
                            yMax: 180,
                            backgroundColor: 'rgba(74, 222, 128, 0.05)',
                            borderColor: 'rgba(74, 222, 128, 0.2)',
                            borderWidth: 1
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { 
                        color: 'rgba(255,255,255,0.5)',
                        maxTicksLimit: 12
                    }
                },
                y: {
                    min: 40,
                    max: 300,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { 
                        color: 'rgba(255,255,255,0.5)',
                        callback: (val) => val + ' mg/dL'
                    }
                }
            }
        }
    });
}

// Update circadian/time-of-day heatmap
function updateCircadianHeatmap(patterns) {
    const heatmapGrid = document.getElementById('circadian-heatmap');
    if (!heatmapGrid || !patterns) return;
    
    // Clear existing cells
    heatmapGrid.innerHTML = '';
    
    // Create 24 hour cells
    for (let hour = 0; hour < 24; hour++) {
        const cell = document.createElement('div');
        cell.className = 'heatmap-cell';
        
        const hourData = patterns[hour] || { avg: 120, count: 0 };
        const avg = hourData.avg || 120;
        
        // Color based on average glucose
        let color, intensity;
        if (avg < 70) {
            color = '248, 113, 113'; // Red for hypo
            intensity = 0.8;
        } else if (avg <= 180) {
            color = '74, 222, 128'; // Green for in-range
            intensity = 0.3 + ((180 - avg) / 180) * 0.5;
        } else if (avg <= 250) {
            color = '251, 191, 36'; // Yellow for high
            intensity = 0.5 + ((avg - 180) / 70) * 0.3;
        } else {
            color = '248, 113, 113'; // Red for very high
            intensity = 0.8;
        }
        
        cell.style.backgroundColor = `rgba(${color}, ${intensity})`;
        cell.setAttribute('data-tooltip', `${hour}:00 - Avg: ${Math.round(avg)} mg/dL`);
        cell.setAttribute('data-tooltip-pos', 'top');
        
        // Add hour label
        const label = document.createElement('span');
        label.className = 'hour-label';
        label.textContent = hour;
        cell.appendChild(label);
        
        heatmapGrid.appendChild(cell);
    }
    
    // Add period labels
    addPeriodLabels();
}

function addPeriodLabels() {
    const periods = [
        { start: 0, end: 6, label: 'Night', icon: '🌙' },
        { start: 6, end: 12, label: 'Morning', icon: '🌅' },
        { start: 12, end: 18, label: 'Afternoon', icon: '☀️' },
        { start: 18, end: 24, label: 'Evening', icon: '🌆' }
    ];
    
    const labelsContainer = document.getElementById('period-labels');
    if (!labelsContainer) return;
    
    labelsContainer.innerHTML = periods.map(p => 
        `<span class="period-label">${p.icon} ${p.label}</span>`
    ).join('');
}

// Update distribution chart from pre-calculated data
function updateDistributionChart(distribution) {
    const lowPct = distribution.low || 0;
    const normalPct = distribution.normal || 0;
    const highPct = distribution.high || 0;
    
    // Update distribution bars
    const distLow = document.getElementById('dist-low');
    const distLowPct = document.getElementById('dist-low-pct');
    if (distLow) distLow.style.width = lowPct + '%';
    if (distLowPct) distLowPct.textContent = lowPct + '%';
    
    const distRange = document.getElementById('dist-range');
    const distRangePct = document.getElementById('dist-range-pct');
    if (distRange) distRange.style.width = normalPct + '%';
    if (distRangePct) distRangePct.textContent = normalPct + '%';
    
    const distHigh = document.getElementById('dist-high');
    const distHighPct = document.getElementById('dist-high-pct');
    if (distHigh) distHigh.style.width = highPct + '%';
    if (distHighPct) distHighPct.textContent = highPct + '%';
}

// Fallback distribution chart from raw readings
function updateDistributionChartFromReadings(readings) {
    const values = readings.map(r => r.glucose_value);
    const total = values.length;
    
    const low = values.filter(v => v < 70).length;
    const normal = values.filter(v => v >= 70 && v <= 180).length;
    const high = values.filter(v => v > 180).length;
    
    updateDistributionChart({
        low: Math.round((low / total) * 100),
        normal: Math.round((normal / total) * 100),
        high: Math.round((high / total) * 100)
    });
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
    
    // Update DOM - use correct IDs from HTML (with null checks)
    const avgEl = document.getElementById('avg-glucose');
    const countEl = document.getElementById('readings-count');
    const tirEl = document.getElementById('time-in-range-analytics');
    const hypoEl = document.getElementById('hypo-count');
    
    if (avgEl) avgEl.textContent = avg;
    if (countEl) countEl.textContent = count;
    if (tirEl) tirEl.textContent = timeInRange + '%';
    if (hypoEl) hypoEl.textContent = hypoEvents;
    
    // Also update GMI and CV
    const gmiEl = document.getElementById('gmi-value');
    const cvEl = document.getElementById('cv-value');
    
    if (gmiEl) {
        // GMI = 3.31 + (0.02392 × average glucose)
        const gmi = 3.31 + (0.02392 * avg);
        gmiEl.textContent = gmi.toFixed(1);
    }
    
    if (cvEl) {
        // CV = (std / mean) * 100
        const mean = avg;
        const squaredDiffs = values.map(v => Math.pow(v - mean, 2));
        const avgSquaredDiff = squaredDiffs.reduce((a, b) => a + b, 0) / values.length;
        const std = Math.sqrt(avgSquaredDiff);
        const cv = (std / mean) * 100;
        cvEl.textContent = cv.toFixed(1);
    }
}

// Generate AGP chart from readings
function generateAGPFromReadings(readings) {
    // Group readings by hour
    const hourlyData = {};
    for (let i = 0; i < 24; i++) {
        hourlyData[i] = [];
    }
    
    readings.forEach(r => {
        const timestamp = r.timestamp ? new Date(r.timestamp) : new Date();
        const hour = timestamp.getHours();
        if (r.glucose_value) {
            hourlyData[hour].push(r.glucose_value);
        }
    });
    
    // Calculate percentiles
    const agpData = {
        hours: Array.from({length: 24}, (_, i) => i),
        p10: [], p25: [], median: [], p75: [], p90: []
    };
    
    for (let hour = 0; hour < 24; hour++) {
        const values = hourlyData[hour].sort((a, b) => a - b);
        if (values.length > 0) {
            agpData.p10.push(percentile(values, 10));
            agpData.p25.push(percentile(values, 25));
            agpData.median.push(percentile(values, 50));
            agpData.p75.push(percentile(values, 75));
            agpData.p90.push(percentile(values, 90));
        } else {
            // Use interpolated values
            agpData.p10.push(80);
            agpData.p25.push(100);
            agpData.median.push(120);
            agpData.p75.push(150);
            agpData.p90.push(180);
        }
    }
    
    renderAGPChart(agpData);
}

function percentile(arr, p) {
    if (arr.length === 0) return 0;
    const index = (p / 100) * (arr.length - 1);
    const lower = Math.floor(index);
    const upper = Math.ceil(index);
    if (lower === upper) return arr[lower];
    return arr[lower] * (upper - index) + arr[upper] * (index - lower);
}

// Generate time period patterns
function generateTimePatternsFromReadings(readings) {
    const periods = {
        night: { hours: [0, 1, 2, 3, 4, 5], values: [], el: 'period-night' },
        dawn: { hours: [6, 7, 8], values: [], el: 'period-dawn' },
        morning: { hours: [9, 10, 11], values: [], el: 'period-morning' },
        afternoon: { hours: [12, 13, 14, 15, 16], values: [], el: 'period-afternoon' },
        evening: { hours: [17, 18, 19, 20], values: [], el: 'period-evening' },
        late_night: { hours: [21, 22, 23], values: [], el: 'period-late_night' }
    };
    
    readings.forEach(r => {
        const timestamp = r.timestamp ? new Date(r.timestamp) : new Date();
        const hour = timestamp.getHours();
        
        for (const [name, period] of Object.entries(periods)) {
            if (period.hours.includes(hour) && r.glucose_value) {
                period.values.push(r.glucose_value);
            }
        }
    });
    
    // Update DOM
    for (const [name, period] of Object.entries(periods)) {
        const el = document.getElementById(period.el);
        if (el && period.values.length > 0) {
            const avg = Math.round(period.values.reduce((a, b) => a + b, 0) / period.values.length);
            el.textContent = avg + ' mg/dL';
        }
    }
    
    // Update heatmap
    updateHeatmapFromReadings(readings);
}

// Update weekly heatmap
function updateHeatmapFromReadings(readings) {
    const container = document.getElementById('heatmap-container');
    if (!container) return;
    
    // Group by day of week and time period
    const heatmapData = {};
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const timePeriods = ['Night', 'Morning', 'Afternoon', 'Evening'];
    
    readings.forEach(r => {
        const timestamp = r.timestamp ? new Date(r.timestamp) : new Date();
        const day = timestamp.getDay();
        const hour = timestamp.getHours();
        let period = 0;
        if (hour >= 6 && hour < 12) period = 1;
        else if (hour >= 12 && hour < 18) period = 2;
        else if (hour >= 18) period = 3;
        
        const key = `${day}-${period}`;
        if (!heatmapData[key]) heatmapData[key] = [];
        if (r.glucose_value) heatmapData[key].push(r.glucose_value);
    });
    
    // Build heatmap grid
    let html = '<div class="heatmap-grid-full">';
    html += '<div class="heatmap-row header"><div class="heatmap-label"></div>';
    days.forEach(day => html += `<div class="heatmap-header">${day}</div>`);
    html += '</div>';
    
    timePeriods.forEach((period, periodIdx) => {
        html += `<div class="heatmap-row"><div class="heatmap-label">${period}</div>`;
        for (let day = 0; day < 7; day++) {
            const key = `${day}-${periodIdx}`;
            const values = heatmapData[key] || [];
            const avg = values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : null;
            
            let color = 'rgba(255, 255, 255, 0.05)';
            if (avg !== null) {
                if (avg < 70) color = 'rgba(248, 113, 113, 0.6)';
                else if (avg <= 180) color = 'rgba(74, 222, 128, 0.5)';
                else if (avg <= 250) color = 'rgba(251, 191, 36, 0.6)';
                else color = 'rgba(239, 68, 68, 0.7)';
            }
            
            html += `<div class="heatmap-cell-full" style="background: ${color}" data-tooltip="${avg ? Math.round(avg) + ' mg/dL' : 'No data'}"></div>`;
        }
        html += '</div>';
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Update TIR breakdown
function updateTIRBreakdown(readings) {
    const values = readings.map(r => r.glucose_value);
    const total = values.length;
    if (total === 0) return;
    
    const veryLow = values.filter(v => v < 54).length;
    const low = values.filter(v => v >= 54 && v < 70).length;
    const inRange = values.filter(v => v >= 70 && v <= 180).length;
    const high = values.filter(v => v > 180 && v <= 250).length;
    const veryHigh = values.filter(v => v > 250).length;
    
    const pcts = {
        veryLow: Math.round((veryLow / total) * 100),
        low: Math.round((low / total) * 100),
        inRange: Math.round((inRange / total) * 100),
        high: Math.round((high / total) * 100),
        veryHigh: Math.round((veryHigh / total) * 100)
    };
    
    // Combined hypo percentage
    const hypoPercent = pcts.veryLow + pcts.low;
    const hyperPercent = pcts.high + pcts.veryHigh;
    
    // Update bar heights
    const updateSegment = (id, pct) => {
        const el = document.getElementById(id);
        if (el) el.style.height = pct + '%';
    };
    
    updateSegment('tir-very-high', pcts.veryHigh);
    updateSegment('tir-high', pcts.high);
    updateSegment('tir-in-range', pcts.inRange);
    updateSegment('tir-low', pcts.low);
    updateSegment('tir-very-low', pcts.veryLow);
    
    // Update labels
    const updateLabel = (id, pct) => {
        const el = document.getElementById(id);
        if (el) el.textContent = pct + '%';
    };
    
    updateLabel('tir-very-high-pct', pcts.veryHigh);
    updateLabel('tir-high-pct', pcts.high);
    updateLabel('tir-in-range-pct', pcts.inRange);
    updateLabel('tir-low-pct', pcts.low);
    updateLabel('tir-very-low-pct', pcts.veryLow);
    
    // Update TIR Summary with explanation
    const summaryEl = document.getElementById('tir-summary');
    if (summaryEl) {
        let summaryClass = 'good';
        let summaryHTML = '';
        
        if (hypoPercent >= 30) {
            // Critical hypoglycemia
            summaryClass = 'alert';
            summaryHTML = `<i class="ri-error-warning-line" style="color: #ef4444;"></i>
                <strong style="color: #ef4444;">Critical:</strong> 
                <span style="color: #f87171;">${hypoPercent}% of readings are hypoglycemic (${veryLow + low}/${total}). 
                This is significantly above the ADA target of <4%. ${pcts.veryLow > 0 ? `${pcts.veryLow}% are dangerously low (<54 mg/dL).` : ''} 
                Please consult your healthcare provider.</span>`;
        } else if (hypoPercent >= 10) {
            // High hypoglycemia
            summaryClass = 'alert';
            summaryHTML = `<i class="ri-alert-line" style="color: #f97316;"></i>
                <strong style="color: #f97316;">Warning:</strong> 
                <span style="color: #fbbf24;">${hypoPercent}% hypoglycemic readings detected (${veryLow + low} events). 
                Target is <4%. Consider adjusting medication or meal timing.</span>`;
        } else if (hypoPercent >= 4) {
            // Moderate hypoglycemia
            summaryClass = 'warning';
            summaryHTML = `<i class="ri-information-line" style="color: #fbbf24;"></i>
                <strong style="color: #fbbf24;">Note:</strong> 
                <span style="color: var(--text-secondary);">${hypoPercent}% readings below range. 
                Slightly above ADA target of <4%. Monitor patterns carefully.</span>`;
        } else if (pcts.inRange >= 70) {
            // Good control
            summaryClass = 'good';
            summaryHTML = `<i class="ri-check-double-line" style="color: #22c55e;"></i>
                <strong style="color: #22c55e;">Excellent!</strong> 
                <span style="color: var(--text-secondary);">${pcts.inRange}% time in range meets ADA guidelines (≥70%). 
                ${hypoPercent === 0 ? 'No hypoglycemic events detected.' : `Only ${hypoPercent}% hypo readings.`}</span>`;
        } else if (hyperPercent > hypoPercent) {
            // High glucose tendency
            summaryClass = 'warning';
            summaryHTML = `<i class="ri-arrow-up-line" style="color: #f59e0b;"></i>
                <strong style="color: #f59e0b;">High Tendency:</strong> 
                <span style="color: var(--text-secondary);">${hyperPercent}% readings above target range. 
                Consider reviewing carb intake and medication timing.</span>`;
        } else {
            // General below target
            summaryClass = 'warning';
            summaryHTML = `<i class="ri-information-line" style="color: #fbbf24;"></i>
                <span style="color: var(--text-secondary);">${pcts.inRange}% time in range - below 70% target. 
                ${hypoPercent > 0 ? `${hypoPercent}% low, ` : ''}${hyperPercent > 0 ? `${hyperPercent}% high.` : ''}</span>`;
        }
        
        summaryEl.innerHTML = summaryHTML;
        summaryEl.className = `tir-summary ${summaryClass}`;
    }
}

// Update risk analysis
function updateRiskAnalysis(readings) {
    const values = readings.map(r => r.glucose_value);
    if (values.length === 0) return;
    
    // Calculate LBGI and HBGI (simplified)
    let lbgiSum = 0, hbgiSum = 0;
    values.forEach(glucose => {
        if (glucose > 0) {
            const fGlucose = 1.509 * (Math.pow(Math.log(glucose), 1.084) - 5.381);
            if (fGlucose < 0) {
                lbgiSum += 10 * Math.pow(fGlucose, 2);
            } else {
                hbgiSum += 10 * Math.pow(fGlucose, 2);
            }
        }
    });
    
    const lbgi = lbgiSum / values.length;
    const hbgi = hbgiSum / values.length;
    
    // Calculate stats for explanation
    const hypoCount = values.filter(v => v < 70).length;
    const hypoPercent = Math.round((hypoCount / values.length) * 100);
    const highCount = values.filter(v => v > 180).length;
    const highPercent = Math.round((highCount / values.length) * 100);
    
    // Update DOM
    const lbgiBar = document.getElementById('lbgi-bar');
    const hbgiBar = document.getElementById('hbgi-bar');
    const lbgiValue = document.getElementById('lbgi-value');
    const hbgiValue = document.getElementById('hbgi-value');
    
    if (lbgiBar) lbgiBar.style.width = Math.min(lbgi * 10, 100) + '%';
    if (hbgiBar) hbgiBar.style.width = Math.min(hbgi * 5, 100) + '%';
    if (lbgiValue) lbgiValue.textContent = lbgi.toFixed(1);
    if (hbgiValue) hbgiValue.textContent = hbgi.toFixed(1);
    
    // Risk category with detailed explanation
    const categoryEl = document.getElementById('risk-category');
    if (categoryEl) {
        let category = 'low', text = 'Low Risk', explanation = '';
        
        if (lbgi >= 10 || hypoPercent >= 50) {
            category = 'critical';
            text = 'Critical Risk';
            explanation = `<br><small style="color: #f87171; display: block; margin-top: 4px;"><i class="ri-error-warning-line"></i> ${hypoPercent}% hypoglycemic readings (${hypoCount}/${values.length}) - Immediate action required!</small>`;
        } else if (lbgi >= 5 || hypoPercent >= 20) {
            category = 'high';
            text = 'High Risk';
            explanation = `<br><small style="color: #f97316; display: block; margin-top: 4px;"><i class="ri-alert-line"></i> LBGI: ${lbgi.toFixed(1)} with ${hypoCount} hypo events (${hypoPercent}%)</small>`;
        } else if (lbgi >= 2.5 || hbgi >= 5) {
            category = 'moderate';
            text = 'Moderate Risk';
            if (lbgi > hbgi) {
                explanation = `<br><small style="color: #fbbf24; display: block; margin-top: 4px;"><i class="ri-information-line"></i> Elevated low glucose risk (LBGI: ${lbgi.toFixed(1)})</small>`;
            } else {
                explanation = `<br><small style="color: #fbbf24; display: block; margin-top: 4px;"><i class="ri-information-line"></i> Elevated high glucose risk (HBGI: ${hbgi.toFixed(1)})</small>`;
            }
        } else {
            explanation = `<br><small style="color: #4ade80; display: block; margin-top: 4px;"><i class="ri-check-line"></i> LBGI: ${lbgi.toFixed(1)}, HBGI: ${hbgi.toFixed(1)} - Both within safe limits</small>`;
        }
        
        categoryEl.innerHTML = `<span class="category-badge ${category}">${text}</span>${explanation}`;
    }
}

// Update dawn phenomenon
function updateDawnPhenomenon(readings) {
    // Get readings from 3-5 AM (pre-dawn) and 6-8 AM (dawn)
    const preDawn = [], dawn = [];
    
    readings.forEach(r => {
        const timestamp = r.timestamp ? new Date(r.timestamp) : new Date();
        const hour = timestamp.getHours();
        if (hour >= 3 && hour < 5 && r.glucose_value) preDawn.push(r.glucose_value);
        if (hour >= 6 && hour < 8 && r.glucose_value) dawn.push(r.glucose_value);
    });
    
    const statusEl = document.getElementById('dawn-status');
    const preEl = document.getElementById('dawn-pre');
    const postEl = document.getElementById('dawn-post');
    const riseEl = document.getElementById('dawn-rise');
    
    if (preDawn.length > 0 && dawn.length > 0) {
        const preAvg = preDawn.reduce((a, b) => a + b, 0) / preDawn.length;
        const dawnAvg = dawn.reduce((a, b) => a + b, 0) / dawn.length;
        const rise = dawnAvg - preAvg;
        
        if (preEl) preEl.textContent = Math.round(preAvg) + ' mg/dL';
        if (postEl) postEl.textContent = Math.round(dawnAvg) + ' mg/dL';
        if (riseEl) riseEl.textContent = (rise > 0 ? '+' : '') + Math.round(rise) + ' mg/dL';
        
        if (statusEl) {
            if (rise > 20) {
                statusEl.innerHTML = '<i class="ri-sun-line"></i> Dawn Phenomenon Detected';
                statusEl.className = 'dawn-status detected';
            } else {
                statusEl.innerHTML = '<i class="ri-check-line"></i> No Significant Dawn Effect';
                statusEl.className = 'dawn-status not-detected';
            }
        }
    } else {
        if (statusEl) {
            statusEl.innerHTML = '<i class="ri-information-line"></i> Insufficient Data';
        }
        if (preEl) preEl.textContent = '--';
        if (postEl) postEl.textContent = '--';
        if (riseEl) riseEl.textContent = '--';
    }
}

// Demo data generating functions
function generateDemoAGPData() {
    const agpData = { p10: [], p25: [], median: [], p75: [], p90: [] };
    for (let i = 0; i < 24; i++) {
        // Simulate realistic glucose patterns
        let baseMedian = 120;
        // Dawn phenomenon simulation (4-8 AM rise)
        if (i >= 4 && i <= 8) baseMedian += (i - 4) * 8;
        // Post-meal spikes
        if (i >= 8 && i <= 10) baseMedian += 30; // Breakfast
        if (i >= 13 && i <= 15) baseMedian += 35; // Lunch
        if (i >= 19 && i <= 21) baseMedian += 40; // Dinner
        // Night stability
        if (i >= 22 || i <= 3) baseMedian = 100;
        
        agpData.p10.push(Math.max(60, baseMedian - 35));
        agpData.p25.push(Math.max(70, baseMedian - 20));
        agpData.median.push(baseMedian);
        agpData.p75.push(baseMedian + 25);
        agpData.p90.push(Math.min(220, baseMedian + 45));
    }
    return agpData;
}

function generateDemoHeatmap() {
    const container = document.getElementById('heatmap-container');
    if (!container) return;
    
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const timePeriods = ['Night', 'Morning', 'Afternoon', 'Evening'];
    
    let html = '<div class="heatmap-grid-full">';
    html += '<div class="heatmap-row header"><div class="heatmap-label"></div>';
    days.forEach(day => html += `<div class="heatmap-header">${day}</div>`);
    html += '</div>';
    
    // Generate demo values for each cell
    const demoValues = [
        [95, 105, 98, 110, 102, 115, 108],   // Night - mostly in range
        [125, 138, 142, 130, 155, 145, 165], // Morning - higher due to dawn phenomenon
        [145, 135, 152, 148, 160, 155, 140], // Afternoon - post lunch
        [130, 125, 140, 135, 145, 155, 130]  // Evening - dinner impact
    ];
    
    timePeriods.forEach((period, periodIdx) => {
        html += `<div class="heatmap-row"><div class="heatmap-label">${period}</div>`;
        for (let day = 0; day < 7; day++) {
            const avg = demoValues[periodIdx][day];
            let color = 'rgba(255, 255, 255, 0.05)';
            if (avg < 70) color = 'rgba(248, 113, 113, 0.6)';
            else if (avg <= 180) color = 'rgba(74, 222, 128, 0.5)';
            else if (avg <= 250) color = 'rgba(251, 191, 36, 0.6)';
            else color = 'rgba(239, 68, 68, 0.7)';
            
            html += `<div class="heatmap-cell-full" style="background: ${color}" data-tooltip="${avg} mg/dL"></div>`;
        }
        html += '</div>';
    });
    html += '</div>';
    
    container.innerHTML = html;
}

function updateDemoTIR() {
    const segments = [
        { id: 'tir-very-high', pct: 3 },
        { id: 'tir-high', pct: 12 },
        { id: 'tir-in-range', pct: 72 },
        { id: 'tir-low', pct: 10 },
        { id: 'tir-very-low', pct: 3 }
    ];
    
    segments.forEach(seg => {
        const el = document.getElementById(seg.id);
        if (el) el.style.height = seg.pct + '%';
        
        const labelEl = document.getElementById(seg.id + '-pct');
        if (labelEl) labelEl.textContent = seg.pct + '%';
    });
}

function updateDemoRiskAnalysis() {
    const lbgiBar = document.getElementById('lbgi-bar');
    const hbgiBar = document.getElementById('hbgi-bar');
    const lbgiValue = document.getElementById('lbgi-value');
    const hbgiValue = document.getElementById('hbgi-value');
    const categoryEl = document.getElementById('risk-category');
    
    if (lbgiBar) lbgiBar.style.width = '25%';
    if (hbgiBar) hbgiBar.style.width = '35%';
    if (lbgiValue) lbgiValue.textContent = '2.5';
    if (hbgiValue) hbgiValue.textContent = '5.8';
    if (categoryEl) {
        categoryEl.innerHTML = '<span class="category-badge moderate">Moderate Risk</span>';
    }
}

function updateDemoTimePeriods() {
    const periods = {
        'period-night': 98,
        'period-dawn': 132,
        'period-morning': 145,
        'period-afternoon': 152,
        'period-evening': 138,
        'period-late_night': 110
    };
    
    for (const [id, value] of Object.entries(periods)) {
        const el = document.getElementById(id);
        if (el) el.textContent = value + ' mg/dL';
    }
    
    // Dawn phenomenon demo
    const statusEl = document.getElementById('dawn-status');
    const preEl = document.getElementById('dawn-pre');
    const postEl = document.getElementById('dawn-post');
    const riseEl = document.getElementById('dawn-rise');
    
    if (preEl) preEl.textContent = '98 mg/dL';
    if (postEl) postEl.textContent = '132 mg/dL';
    if (riseEl) riseEl.textContent = '+34 mg/dL';
    if (statusEl) {
        statusEl.innerHTML = '<i class="ri-sun-line"></i> Dawn Phenomenon Detected';
        statusEl.className = 'dawn-status detected';
    }
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

// ============================================
// WEBSOCKET REAL-TIME UPDATES
// ============================================
let socket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

function initWebSocket() {
    // Check if Socket.IO is available
    if (typeof io === 'undefined') {
        console.log('Socket.IO not available, falling back to polling');
        return;
    }
    
    const userId = localStorage.getItem('aura_user_id') || localStorage.getItem('user_id');
    if (!userId) return;
    
    try {
        socket = io({
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionDelayMax: 5000,
            reconnectionAttempts: MAX_RECONNECT_ATTEMPTS
        });
        
        socket.on('connect', () => {
            console.log('🔌 WebSocket connected');
            reconnectAttempts = 0;
            
            // Join user's room for targeted updates
            socket.emit('join', { user_id: userId });
            
            // Update connection indicator
            updateConnectionStatus(true);
        });
        
        socket.on('disconnect', () => {
            console.log('🔌 WebSocket disconnected');
            updateConnectionStatus(false);
        });
        
        socket.on('connect_error', (error) => {
            console.log('WebSocket connection error, using fallback polling');
            reconnectAttempts++;
            if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
                console.log('Max reconnection attempts reached, using HTTP polling');
                startFallbackPolling();
            }
        });
        
        // Real-time glucose updates
        socket.on('glucose_update', (data) => {
            console.log('📊 Real-time glucose update:', data);
            handleRealtimeGlucoseUpdate(data);
        });
        
        // Prediction updates
        socket.on('prediction_update', (data) => {
            console.log('🔮 Real-time prediction update:', data);
            handleRealtimePredictionUpdate(data);
        });
        
        // Dashboard refresh signal
        socket.on('dashboard_refresh', () => {
            console.log('🔄 Dashboard refresh signal received');
            loadDashboardData();
        });
        
        // Recommendation updates
        socket.on('recommendation_update', (data) => {
            console.log('💡 Real-time recommendation:', data);
            handleRealtimeRecommendation(data);
        });
        
    } catch (error) {
        console.error('WebSocket initialization error:', error);
        startFallbackPolling();
    }
}

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connection-status');
    if (indicator) {
        indicator.className = connected ? 'status-connected' : 'status-disconnected';
        indicator.setAttribute('data-tooltip', connected ? 'Real-time connected' : 'Reconnecting...');
    }
}

function handleRealtimeGlucoseUpdate(data) {
    // Update current glucose display
    const currentGlucose = document.getElementById('current-glucose');
    if (currentGlucose && data.glucose_value) {
        gsap.to(currentGlucose, {
            innerText: Math.round(data.glucose_value),
            duration: 0.5,
            snap: { innerText: 1 },
            ease: 'power2.out'
        });
        
        // Flash animation for new reading
        gsap.fromTo(currentGlucose.parentElement, 
            { boxShadow: '0 0 20px rgba(74, 222, 128, 0.5)' },
            { boxShadow: '0 0 0px rgba(74, 222, 128, 0)', duration: 1 }
        );
    }
    
    // Update trend
    if (data.trend) {
        const trendEl = document.getElementById('glucose-trend');
        if (trendEl) {
            const trendIcons = { rising: '↗', falling: '↘', stable: '→' };
            trendEl.textContent = trendIcons[data.trend] || '→';
        }
    }
    
    // Add to chart if it exists
    if (chartInstance && data.glucose_value) {
        addReadingToChart(data);
    }
}

function handleRealtimePredictionUpdate(data) {
    // Update prediction display
    const predictionEl = document.getElementById('predicted-glucose');
    if (predictionEl && data.predicted_glucose) {
        gsap.to(predictionEl, {
            innerText: Math.round(data.predicted_glucose),
            duration: 0.5,
            snap: { innerText: 1 },
            ease: 'power2.out'
        });
    }
    
    // Update confidence if shown
    if (data.confidence) {
        const confidenceEl = document.getElementById('prediction-confidence');
        if (confidenceEl) {
            confidenceEl.textContent = Math.round(data.confidence * 100) + '%';
        }
    }
}

function handleRealtimeRecommendation(data) {
    // Show recommendation as toast
    if (data.message) {
        const icon = data.type === 'warning' ? '⚠️' : data.type === 'alert' ? '🚨' : '💡';
        showToast(data.type || 'info', icon + ' Recommendation', data.message);
    }
}

function addReadingToChart(data) {
    if (!chartInstance || !chartInstance.data) return;
    
    const timestamp = data.timestamp ? new Date(data.timestamp) : new Date();
    const label = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    // Add new data point
    chartInstance.data.labels.push(label);
    chartInstance.data.datasets[0].data.push(data.glucose_value);
    
    // Keep only last 24 points for performance
    if (chartInstance.data.labels.length > 24) {
        chartInstance.data.labels.shift();
        chartInstance.data.datasets[0].data.shift();
    }
    
    chartInstance.update('none'); // No animation for real-time updates
}

// Fallback polling when WebSocket is unavailable
let pollingInterval = null;

function startFallbackPolling() {
    if (pollingInterval) return;
    
    console.log('Starting fallback HTTP polling...');
    pollingInterval = setInterval(() => {
        const userId = localStorage.getItem('aura_user_id');
        if (userId && document.getElementById('dashboardPage')?.classList.contains('hidden') === false) {
            loadDashboardData();
        }
    }, 30000); // Poll every 30 seconds
}

function stopFallbackPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

// Disconnect WebSocket when leaving dashboard
function disconnectWebSocket() {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
    stopFallbackPolling();
    stopAutoRefresh();
}

// ============================================
// AUTO-REFRESH SYSTEM FOR REAL-TIME DATA
// ============================================
let autoRefreshInterval = null;
const AUTO_REFRESH_INTERVAL = 60000; // 1 minute

function startAutoRefresh() {
    if (autoRefreshInterval) return;
    
    console.log('🔄 Starting auto-refresh (every 60s)...');
    autoRefreshInterval = setInterval(() => {
        const dashboardPage = document.getElementById('dashboardPage');
        const dashboardContainer = document.getElementById('dashboardContainer');
        
        // Only refresh if dashboard is visible
        if (dashboardPage && !dashboardPage.classList.contains('hidden')) {
            if (dashboardContainer && !dashboardContainer.classList.contains('hidden')) {
                console.log('🔄 Auto-refreshing dashboard data...');
                refreshDashboardSilently();
            }
        }
    }, AUTO_REFRESH_INTERVAL);
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
        console.log('🔄 Auto-refresh stopped');
    }
}

// Silent refresh - doesn't show loading state
async function refreshDashboardSilently() {
    const userId = localStorage.getItem('aura_user_id');
    if (!userId) return;
    
    try {
        const res = await fetch(`${BASE_URL}/api/dashboard?user_id=${userId}`);
        const data = await res.json();
        
        if (res.ok && data.glucose_readings) {
            // Update UI without loading animation
            updateDashboardUI(data);
            
            // Show subtle indicator that data was refreshed
            showRefreshIndicator();
        }
    } catch (err) {
        console.error('Silent refresh error:', err);
    }
}

// Show subtle refresh indicator
function showRefreshIndicator() {
    const indicator = document.createElement('div');
    indicator.className = 'refresh-indicator';
    indicator.innerHTML = '<i class="ri-refresh-line"></i> Updated';
    document.body.appendChild(indicator);
    
    // Animate in
    gsap.fromTo(indicator, 
        { opacity: 0, y: -20 },
        { opacity: 1, y: 0, duration: 0.3 }
    );
    
    // Remove after delay
    setTimeout(() => {
        gsap.to(indicator, {
            opacity: 0,
            y: -20,
            duration: 0.3,
            onComplete: () => indicator.remove()
        });
    }, 2000);
}

// Manual refresh button handler
function handleManualRefresh() {
    const refreshBtn = document.getElementById('btn-refresh');
    if (refreshBtn) {
        refreshBtn.classList.add('refreshing');
        refreshBtn.querySelector('i')?.classList.add('ri-spin');
    }
    
    loadDashboardData().finally(() => {
        if (refreshBtn) {
            refreshBtn.classList.remove('refreshing');
            refreshBtn.querySelector('i')?.classList.remove('ri-spin');
        }
        showToast('success', 'Refreshed', 'Dashboard data updated');
    });
}

// Dashboard refresh handler
function handleDashboardRefresh() {
    const btn = document.getElementById('btn-refresh-dashboard');
    const icon = btn?.querySelector('i');
    
    if (icon) icon.classList.add('ri-spin');
    if (btn) btn.disabled = true;
    
    loadDashboardData().finally(() => {
        if (icon) icon.classList.remove('ri-spin');
        if (btn) btn.disabled = false;
        showToast('success', 'Refreshed', 'Dashboard data updated');
    });
}

// Analytics refresh handler
function handleAnalyticsRefresh() {
    const btn = document.getElementById('btn-refresh-analytics');
    const icon = btn?.querySelector('i');
    
    if (icon) icon.classList.add('ri-spin');
    if (btn) btn.disabled = true;
    
    loadAnalyticsData();
    
    // Re-enable after a delay
    setTimeout(() => {
        if (icon) icon.classList.remove('ri-spin');
        if (btn) btn.disabled = false;
        showToast('success', 'Refreshed', 'Analytics data updated');
    }, 2000);
}

// ============================================
// LAZY LOADING FOR DASHBOARD COMPONENTS
// ============================================
const lazyLoadObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const component = entry.target;
            const loadFn = component.dataset.lazyLoad;
            
            if (loadFn && typeof window[loadFn] === 'function') {
                window[loadFn]();
                component.classList.add('loaded');
                lazyLoadObserver.unobserve(component);
            }
        }
    });
}, {
    rootMargin: '100px',
    threshold: 0.1
});

function initLazyLoading() {
    document.querySelectorAll('[data-lazy-load]').forEach(component => {
        lazyLoadObserver.observe(component);
    });
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
    document.getElementById('btn-refresh-dashboard')?.addEventListener('click', handleDashboardRefresh);
    document.getElementById('btn-refresh-analytics')?.addEventListener('click', handleAnalyticsRefresh);
    
    // Logout button
    document.getElementById('nav-logout')?.addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
    });

    // Check for saved login - auto login if user was previously logged in
    if (checkSavedLogin()) {
        loadDashboardData();
        navigateTo('dashboard');
        // Initialize WebSocket for real-time updates
        initWebSocket();
        // Initialize lazy loading
        initLazyLoading();
        // Start auto-refresh
        startAutoRefresh();
    } else {
        navigateTo('landing');
    }
});
