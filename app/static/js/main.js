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
  
  // Close all dropdowns initially
  document.querySelectorAll('.dropdown-menu').forEach(menu => {
    menu.style.display = 'none';
  });
  
  // Setup dropdown handlers
  setupDropdowns();
  
  // Update dropdown behavior on window resize
  window.addEventListener('resize', function() {
    setupDropdowns();
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
 * Setup dropdown behavior based on screen size
 */
function setupDropdowns() {
  const isMobile = window.innerWidth <= 768;
  const dropdowns = document.querySelectorAll('.dropdown');
  
  // First, remove all existing event listeners (if possible)
  dropdowns.forEach(dropdown => {
    const dropdownLink = dropdown.querySelector('a');
    if (dropdownLink) {
      // Clone and replace to remove event listeners
      const newLink = dropdownLink.cloneNode(true);
      dropdownLink.parentNode.replaceChild(newLink, dropdownLink);
    }
  });
  
  // Setup appropriate event listeners based on screen size
  dropdowns.forEach(dropdown => {
    const dropdownLink = dropdown.querySelector('a');
    const dropdownMenu = dropdown.querySelector('.dropdown-menu');
    
    if (!dropdownLink || !dropdownMenu) return;
    
    if (isMobile) {
      // Mobile: toggle on click
      dropdownLink.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Close all other dropdowns
        document.querySelectorAll('.dropdown-menu').forEach(menu => {
          if (menu !== dropdownMenu) {
            menu.style.display = 'none';
          }
        });
        
        // Toggle this dropdown
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
      });
    } else {
      // Desktop: show on hover
      dropdown.addEventListener('mouseenter', function() {
        dropdownMenu.style.display = 'block';
      });
      
      dropdown.addEventListener('mouseleave', function() {
        dropdownMenu.style.display = 'none';
      });
    }
  });
  
  // Close dropdowns when clicking outside
  document.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown')) {
      document.querySelectorAll('.dropdown-menu').forEach(menu => {
        menu.style.display = 'none';
      });
    }
  });
}

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
