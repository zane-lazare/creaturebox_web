/**
 * Creaturebox Web Interface
 * Main JavaScript file
 */

document.addEventListener('DOMContentLoaded', function() {
  // Mobile menu toggle
  const menuToggle = document.querySelector('.menu-toggle');
  const mainNav = document.querySelector('.main-nav');
  
  if (menuToggle && mainNav) {
    menuToggle.addEventListener('click', function() {
      mainNav.classList.toggle('active');
    });
  }
  
  // Handle dropdowns
  const dropdowns = document.querySelectorAll('.dropdown');
  
  dropdowns.forEach(dropdown => {
    if (window.innerWidth <= 768) {
      // Mobile dropdown behavior
      const link = dropdown.querySelector('a');
      link.addEventListener('click', function(e) {
        e.preventDefault();
        const menu = this.nextElementSibling;
        if (menu) {
          menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
        }
      });
    } else {
      // Desktop dropdown behavior
      dropdown.addEventListener('mouseenter', function() {
        const menu = this.querySelector('.dropdown-menu');
        if (menu) {
          menu.style.display = 'block';
        }
      });
      
      dropdown.addEventListener('mouseleave', function() {
        const menu = this.querySelector('.dropdown-menu');
        if (menu) {
          menu.style.display = 'none';
        }
      });
    }
  });
  
  // Flash message close button
  const closeButtons = document.querySelectorAll('.flash-message .close');
  
  closeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const message = this.parentNode;
      message.style.opacity = '0';
      setTimeout(() => {
        message.style.display = 'none';
      }, 300);
    });
  });
  
  // Add current year to footer
  const currentYearSpan = document.getElementById('current-year');
  if (currentYearSpan) {
    currentYearSpan.textContent = new Date().getFullYear();
  }
  
  // Simulate data for dashboard in development mode ONLY when not using real metrics
  if ((window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') && 
      !window.location.pathname.includes('/system/')) {
    // Only simulate data if we're not on a system page
    if (!document.querySelector('script[data-real-metrics]')) {
      simulateDashboardData();
    }
  }
});

/**
 * Simulate data for dashboard during development
 */
function simulateDashboardData() {
  // System info simulation
  updateSystemInfo('CPU', Math.floor(Math.random() * 100) + '%');
  updateSystemInfo('Memory', Math.floor(Math.random() * 1024) + ' MB');
  updateSystemInfo('Disk', Math.floor(Math.random() * 64) + ' GB');
  updateSystemInfo('Temperature', (Math.random() * 30 + 30).toFixed(1) + '°C');
  updateSystemInfo('Uptime', Math.floor(Math.random() * 30) + 'd ' + 
                         Math.floor(Math.random() * 24) + 'h ' + 
                         Math.floor(Math.random() * 60) + 'm');
  updateSystemInfo('IP Address', '192.168.1.' + Math.floor(Math.random() * 255));
  
  // Storage meter simulation
  const usedPercentage = Math.floor(Math.random() * 80);
  const totalStorage = 64;
  const usedStorage = (totalStorage * usedPercentage / 100).toFixed(1);
  
  const meterBar = document.querySelector('.meter-bar');
  const meterLabel = document.querySelector('.meter-label');
  
  if (meterBar) {
    meterBar.style.width = usedPercentage + '%';
  }
  
  if (meterLabel) {
    meterLabel.textContent = usedPercentage + '% used (' + usedStorage + ' GB of ' + totalStorage + ' GB)';
  }
}

/**
 * Update system info value in dashboard
 */
function updateSystemInfo(label, value) {
  const elements = document.querySelectorAll('.info-item');
  
  elements.forEach(element => {
    const labelElement = element.querySelector('.label');
    if (labelElement && labelElement.textContent === label) {
      const valueElement = element.querySelector('.value');
      if (valueElement) {
        valueElement.textContent = value;
      }
    }
  });
}
