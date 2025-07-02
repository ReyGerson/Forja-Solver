/* ===============================
   THEME MANAGER - DÍA/NOCHE
   FUNCIONA EN TODAS LAS PÁGINAS
   =============================== */

class ThemeManager {
    constructor() {
        this.initTheme();
        this.bindEvents();
    }

    initTheme() {
        // Detectar tema guardado o preferencia del sistema
        const savedTheme = localStorage.getItem('theme');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        let theme = savedTheme;
        if (!theme) {
            theme = systemPrefersDark ? 'dark' : 'light';
        }
        
        this.setTheme(theme);
        this.updateToggleButtons();
    }

    setTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
        } else {
            document.body.classList.remove('dark-theme');
        }
        
        localStorage.setItem('theme', theme);
        this.currentTheme = theme;
    }

    toggleTheme() {
        const newTheme = this.currentTheme === 'dark' ? 'light' : 'dark';
        this.setTheme(newTheme);
        this.updateToggleButtons();
    }

    updateToggleButtons() {
        const buttons = document.querySelectorAll('#themeToggle, #indexThemeToggle, .theme-toggle-btn');
        const isDark = this.currentTheme === 'dark';
        
        buttons.forEach(button => {
            const icon = button.querySelector('.theme-icon');
            if (icon) {
                icon.textContent = isDark ? '☀️' : '🌓';
            }
            
            // Update title attribute
            button.title = isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme';
        });
    }

    bindEvents() {
        // Detectar cambios en la preferencia del sistema
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!localStorage.getItem('theme')) {
                this.setTheme(e.matches ? 'dark' : 'light');
                this.updateToggleButtons();
            }
        });

        // Bind theme toggle buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#themeToggle, #indexThemeToggle') || 
                e.target.closest('#themeToggle, #indexThemeToggle')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });
    }
}

// Initialize theme manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.themeManager = new ThemeManager();
});

// Export for manual usage if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ThemeManager;
}
