/* ============================================
   WorkSphere HR - Main JavaScript
   ============================================ */

'use strict';

// ============ Theme Manager ============
const ThemeManager = {
  init() {
    const saved = localStorage.getItem('ws-theme') || 'light';
    this.setTheme(saved);
    document.getElementById('themeToggle')?.addEventListener('click', () => this.toggle());
  },
  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('ws-theme', theme);
  },
  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.setTheme(current === 'dark' ? 'light' : 'dark');
  }
};

// ============ Sidebar Manager ============
const SidebarManager = {
  init() {
    const toggle = document.getElementById('sidebarToggle');
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('sidebar');

    toggle?.addEventListener('click', () => this.toggleDesktop(sidebar));
    mobileToggle?.addEventListener('click', () => this.toggleMobile(sidebar));

    // Close on outside click (mobile)
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 768 && sidebar?.classList.contains('open')) {
        if (!sidebar.contains(e.target) && !mobileToggle?.contains(e.target)) {
          sidebar.classList.remove('open');
        }
      }
    });

    // Restore state
    const collapsed = localStorage.getItem('ws-sidebar-collapsed') === 'true';
    if (collapsed && window.innerWidth > 768) {
      sidebar?.classList.add('collapsed');
      document.getElementById('mainContent')?.classList.add('sidebar-collapsed');
    }
  },
  toggleDesktop(sidebar) {
    sidebar?.classList.toggle('collapsed');
    document.getElementById('mainContent')?.classList.toggle('sidebar-collapsed');
    const isCollapsed = sidebar?.classList.contains('collapsed');
    localStorage.setItem('ws-sidebar-collapsed', isCollapsed);
  },
  toggleMobile(sidebar) {
    sidebar?.classList.toggle('open');
  }
};

// ============ DateTime Clock ============
const DateTimeClock = {
  init() {
    this.update();
    setInterval(() => this.update(), 1000);
  },
  update() {
    const el = document.getElementById('wsDateTime');
    if (!el) return;
    const now = new Date();
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const time = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const date = `${days[now.getDay()]}, ${now.getDate()} ${months[now.getMonth()]} ${now.getFullYear()}`;
    el.innerHTML = `<span style="font-weight:600">${time}</span> <span style="opacity:0.7;font-size:11px">${date}</span>`;
  }
};

// ============ Live Clock Widget ============
const ClockWidget = {
  init() {
    this.update();
    setInterval(() => this.update(), 1000);
  },
  update() {
    const el = document.getElementById('clockWidgetTime');
    if (!el) return;
    const now = new Date();
    el.textContent = now.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const dateEl = document.getElementById('clockWidgetDate');
    if (dateEl) {
      dateEl.textContent = now.toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    }
  }
};

// ============ Attendance Manager ============
const AttendanceManager = {
  watchId: null,

  init() {
    document.getElementById('clockInBtn')?.addEventListener('click', () => this.clockIn());
    document.getElementById('clockOutBtn')?.addEventListener('click', () => this.clockOut());
    document.getElementById('breakInBtn')?.addEventListener('click', () => this.breakIn());
    document.getElementById('breakOutBtn')?.addEventListener('click', () => this.breakOut());
  },

  getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
           document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1] || '';
  },

  async getLocation() {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve({ latitude: null, longitude: null, address: '' });
        return;
      }
      navigator.geolocation.getCurrentPosition(
        pos => resolve({
          latitude: pos.coords.latitude,
          longitude: pos.coords.longitude,
          address: `${pos.coords.latitude.toFixed(6)}, ${pos.coords.longitude.toFixed(6)}`
        }),
        () => resolve({ latitude: null, longitude: null, address: '' }),
        { enableHighAccuracy: true, timeout: 10000 }
      );
    });
  },

  async captureSelfie() {
    return new Promise((resolve) => {
      // Check if selfie modal exists
      const modal = document.getElementById('selfieModal');
      if (!modal) { resolve(null); return; }

      const video = document.getElementById('selfieVideo');
      const captureBtn = document.getElementById('captureSelfieBtn');
      const canvas = document.getElementById('selfieCanvas');

      navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } })
        .then(stream => {
          video.srcObject = stream;
          video.play();

          const bsModal = new bootstrap.Modal(modal);
          bsModal.show();

          captureBtn.onclick = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            stream.getTracks().forEach(t => t.stop());
            bsModal.hide();
            canvas.toBlob(blob => resolve(blob), 'image/jpeg', 0.8);
          };

          modal.addEventListener('hidden.bs.modal', () => {
            stream.getTracks().forEach(t => t.stop());
            resolve(null);
          }, { once: true });
        })
        .catch(() => resolve(null));
    });
  },

  async clockIn() {
    const btn = document.getElementById('clockInBtn');
    if (!btn) return;

    this.setLoading(btn, true, 'Clocking In...');

    try {
      const location = await this.getLocation();

      const formData = new FormData();
      formData.append('source', 'web');
      if (location.latitude) formData.append('latitude', location.latitude);
      if (location.longitude) formData.append('longitude', location.longitude);
      if (location.address) formData.append('address', location.address);

      // Try selfie capture
      const selfie = await this.captureSelfie();
      if (selfie) formData.append('selfie', selfie, 'selfie.jpg');

      const res = await fetch('/api/v1/attendance/clock-in/', {
        method: 'POST',
        headers: { 'X-CSRFToken': this.getCSRFToken() },
        body: formData
      });

      const data = await res.json();

      if (res.ok && data.success) {
        this.showToast('success', `Clocked in at ${new Date(data.clock_in).toLocaleTimeString()}`);
        this.updateClockStatus('clocked_in', data);
        document.getElementById('clockInBtn')?.setAttribute('disabled', true);
        document.getElementById('clockOutBtn')?.removeAttribute('disabled');
      } else {
        this.showToast('error', data.error || 'Failed to clock in');
      }
    } catch (err) {
      this.showToast('error', 'Network error. Please try again.');
    } finally {
      this.setLoading(btn, false, '<i class="fa-solid fa-right-to-bracket"></i> Clock In');
    }
  },

  async clockOut() {
    const btn = document.getElementById('clockOutBtn');
    if (!btn) return;

    if (!confirm('Are you sure you want to clock out?')) return;

    this.setLoading(btn, true, 'Clocking Out...');

    try {
      const location = await this.getLocation();

      const formData = new FormData();
      formData.append('source', 'web');
      if (location.latitude) formData.append('latitude', location.latitude);
      if (location.longitude) formData.append('longitude', location.longitude);
      if (location.address) formData.append('address', location.address);

      const selfie = await this.captureSelfie();
      if (selfie) formData.append('selfie', selfie, 'selfie.jpg');

      const res = await fetch('/api/v1/attendance/clock-out/', {
        method: 'POST',
        headers: { 'X-CSRFToken': this.getCSRFToken() },
        body: formData
      });

      const data = await res.json();

      if (res.ok && data.success) {
        this.showToast('success', `Clocked out. Working hours: ${data.working_hours}`);
        this.updateClockStatus('clocked_out', data);
        document.getElementById('clockOutBtn')?.setAttribute('disabled', true);
      } else {
        this.showToast('error', data.error || 'Failed to clock out');
      }
    } catch (err) {
      this.showToast('error', 'Network error. Please try again.');
    } finally {
      this.setLoading(btn, false, '<i class="fa-solid fa-right-from-bracket"></i> Clock Out');
    }
  },

  async breakIn() {
    const res = await fetch('/api/v1/attendance/break-in/', {
      method: 'POST',
      headers: { 'X-CSRFToken': this.getCSRFToken(), 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    if (res.ok) this.showToast('info', 'Break started');
    else this.showToast('error', data.error);
  },

  async breakOut() {
    const res = await fetch('/api/v1/attendance/break-out/', {
      method: 'POST',
      headers: { 'X-CSRFToken': this.getCSRFToken(), 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    if (res.ok) this.showToast('info', 'Break ended');
    else this.showToast('error', data.error);
  },

  updateClockStatus(status, data) {
    const statusEl = document.getElementById('attendanceStatus');
    const clockInTimeEl = document.getElementById('clockInTime');
    const clockOutTimeEl = document.getElementById('clockOutTime');
    const workingHoursEl = document.getElementById('workingHours');

    if (status === 'clocked_in') {
      statusEl?.classList.remove('absent');
      statusEl?.classList.add('present');
      statusEl && (statusEl.textContent = 'Present');
      if (clockInTimeEl) clockInTimeEl.textContent = new Date(data.clock_in).toLocaleTimeString();
    } else if (status === 'clocked_out') {
      if (clockOutTimeEl) clockOutTimeEl.textContent = new Date().toLocaleTimeString();
      if (workingHoursEl) workingHoursEl.textContent = data.working_hours;
    }
  },

  setLoading(btn, loading, text) {
    if (loading) {
      btn.disabled = true;
      btn.innerHTML = `<span class="ws-spinner" style="width:16px;height:16px;border-width:2px"></span> ${text}`;
    } else {
      btn.disabled = false;
      btn.innerHTML = text;
    }
  },

  showToast(type, message) {
    const colors = { success: '#10B981', error: '#EF4444', warning: '#F59E0B', info: '#2563EB' };
    const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-circle', info: 'fa-info-circle' };

    const toast = document.createElement('div');
    toast.className = 'ws-toast';
    toast.style.cssText = `
      position: fixed; bottom: 24px; right: 24px; z-index: 9999;
      background: ${colors[type]}; color: white;
      padding: 14px 20px; border-radius: 12px;
      display: flex; align-items: center; gap: 10px;
      font-size: 14px; font-weight: 500; font-family: var(--font-main);
      box-shadow: 0 8px 24px rgba(0,0,0,0.15);
      animation: slideInUp 0.3s ease; max-width: 360px;
    `;
    toast.innerHTML = `<i class="fa-solid ${icons[type]}"></i><span>${message}</span>`;

    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'slideOutDown 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }
};

// ============ Charts Manager ============
const ChartsManager = {
  charts: {},

  createAttendancePieChart(canvasId, data) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.charts[canvasId] = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Present', 'Absent', 'Half Day', 'Leave', 'Holiday'],
        datasets: [{
          data: [data.present, data.absent, data.half_day, data.leave, data.holiday],
          backgroundColor: ['#10B981', '#EF4444', '#8B5CF6', '#2563EB', '#F59E0B'],
          borderWidth: 0,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { position: 'bottom', labels: { padding: 16, usePointStyle: true, font: { family: 'Plus Jakarta Sans', size: 12 } } }
        }
      }
    });
  },

  createAttendanceTrendChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.charts[canvasId] = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: datasets.map((ds, i) => ({
          ...ds,
          borderColor: ['#2563EB', '#10B981', '#F59E0B'][i],
          backgroundColor: ['rgba(37,99,235,0.05)', 'rgba(16,185,129,0.05)', 'rgba(245,158,11,0.05)'][i],
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: ['#2563EB', '#10B981', '#F59E0B'][i],
          tension: 0.4,
          fill: true
        }))
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { usePointStyle: true, font: { family: 'Plus Jakarta Sans', size: 12 } } }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } } },
          y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { font: { family: 'Plus Jakarta Sans', size: 11 } } }
        }
      }
    });
  },

  createPayrollBarChart(canvasId, labels, grossData, netData) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          { label: 'Gross', data: grossData, backgroundColor: 'rgba(37,99,235,0.7)', borderRadius: 6 },
          { label: 'Net', data: netData, backgroundColor: 'rgba(16,185,129,0.7)', borderRadius: 6 }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { usePointStyle: true, font: { family: 'Plus Jakarta Sans', size: 12 } } }
        },
        scales: {
          x: { grid: { display: false } },
          y: {
            grid: { color: 'rgba(0,0,0,0.05)' },
            ticks: { callback: v => '₹' + (v >= 100000 ? (v/100000).toFixed(1) + 'L' : v.toLocaleString('en-IN')) }
          }
        }
      }
    });
  },

  createDeptStrengthChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId)?.getContext('2d');
    if (!ctx) return;

    this.charts[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Employees',
          data,
          backgroundColor: labels.map((_, i) => `hsl(${(i * 37) % 360}, 65%, 55%)`),
          borderRadius: 8,
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { color: 'rgba(0,0,0,0.05)' } },
          y: { grid: { display: false }, ticks: { font: { family: 'Plus Jakarta Sans', size: 12 } } }
        }
      }
    });
  }
};

// ============ Table Search & Sort ============
const TableManager = {
  init(tableId) {
    const searchInput = document.querySelector(`[data-table-search="${tableId}"]`);
    const table = document.getElementById(tableId);
    if (!searchInput || !table) return;

    searchInput.addEventListener('input', () => {
      const query = searchInput.value.toLowerCase();
      const rows = table.querySelectorAll('tbody tr');
      rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
      });
    });
  }
};

// ============ Form Validators ============
const FormValidator = {
  init(formId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', (e) => {
      const invalid = this.validate(form);
      if (invalid.length > 0) {
        e.preventDefault();
        invalid.forEach(el => el.classList.add('is-invalid'));
      }
    });

    form.querySelectorAll('[required]').forEach(el => {
      el.addEventListener('change', () => {
        if (el.value) el.classList.remove('is-invalid');
      });
    });
  },

  validate(form) {
    const invalid = [];
    form.querySelectorAll('[required]').forEach(el => {
      if (!el.value.trim()) invalid.push(el);
    });
    return invalid;
  }
};

// ============ Notification Fetcher ============
const NotificationManager = {
  async fetchCount() {
    try {
      const res = await fetch('/api/v1/notifications/unread-count/');
      const data = await res.json();
      const badge = document.querySelector('.ws-notif-count');
      if (badge) badge.textContent = data.count || 0;
    } catch {}
  },

  init() {
    this.fetchCount();
    setInterval(() => this.fetchCount(), 60000);
  }
};

// ============ Geolocation Map Preview ============
const MapPreview = {
  showLocation(lat, lng, elementId) {
    const el = document.getElementById(elementId);
    if (!el || !lat || !lng) return;
    el.innerHTML = `
      <div style="background:#f0f4ff;border-radius:8px;padding:10px;display:flex;align-items:center;gap:8px">
        <i class="fa-solid fa-location-dot" style="color:#2563EB"></i>
        <span style="font-size:12px;color:#374151">GPS: ${parseFloat(lat).toFixed(5)}, ${parseFloat(lng).toFixed(5)}</span>
        <span class="ws-status present" style="margin-left:auto;font-size:10px">Located</span>
      </div>
    `;
  }
};

// ============ CSS Animations ============
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInUp {
    from { transform: translateY(20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }
  @keyframes slideOutDown {
    from { transform: translateY(0); opacity: 1; }
    to { transform: translateY(20px); opacity: 0; }
  }
  .ws-sidebar.collapsed { width: 72px; }
  .ws-sidebar.collapsed .ws-logo-text,
  .ws-sidebar.collapsed .ws-user-info,
  .ws-sidebar.collapsed .ws-nav-label,
  .ws-sidebar.collapsed .ws-nav-link span,
  .ws-sidebar.collapsed .ws-badge { display: none; }
  .ws-sidebar.collapsed .ws-logo-icon { margin: auto; }
  .ws-sidebar.collapsed .ws-nav-link { justify-content: center; padding: 10px; }
  .ws-sidebar.collapsed .ws-sidebar-user { justify-content: center; }
  .ws-sidebar.collapsed .ws-sidebar-footer .ws-nav-link { justify-content: center; padding: 10px; }
  .ws-main.sidebar-collapsed { margin-left: 72px; }
`;
document.head.appendChild(style);

// ============ Init ============
document.addEventListener('DOMContentLoaded', () => {
  ThemeManager.init();
  SidebarManager.init();
  DateTimeClock.init();
  ClockWidget.init();
  AttendanceManager.init();
  NotificationManager.init();

  // Init table search for any table with data-table attribute
  document.querySelectorAll('[data-table]').forEach(table => {
    TableManager.init(table.id);
  });

  // Init form validators
  document.querySelectorAll('[data-validate]').forEach(form => {
    FormValidator.init(form.id);
  });
});
