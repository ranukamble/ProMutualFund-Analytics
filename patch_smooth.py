import re

def add_smooth_animations():
    file_path = 'templates/index.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    premium_css = """
        /* Premium Smooth Animations & Micro-interactions */
        html { scroll-behavior: smooth; }
        
        body {
            animation: appLoad 0.8s cubic-bezier(0.1, 0.7, 0.1, 1) forwards;
        }
        
        @keyframes appLoad {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Interactive Elements */
        button, .ticker-item, .nav-btn, select, input {
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), background-color 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease, opacity 0.3s ease !important;
        }
        
        button:active, .fund-item:active {
            transform: scale(0.96) !important;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px var(--shadow-alpha);
        }

        /* Cards & Panels Hover Effects */
        .stat-card, .chart-section, .hero-card, .save-card, #pgCardInvested, #pgCardCurrent {
            transition: transform 0.3s cubic-bezier(0.1, 0.7, 0.1, 1), box-shadow 0.3s cubic-bezier(0.1, 0.7, 0.1, 1) !important;
        }
        
        .stat-card:hover, .chart-section:hover, .save-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 16px 32px var(--shadow-alpha);
        }

        /* Sidebar Fund Items */
        .fund-item {
            transition: all 0.3s cubic-bezier(0.1, 0.7, 0.1, 1) !important;
        }
        .fund-item:hover {
            transform: translateX(6px);
            box-shadow: -4px 4px 12px var(--shadow-alpha);
        }

        /* Portfolio Builder Rows */
        #pgSelectedFunds > div {
            transition: all 0.3s ease !important;
        }
        #pgSelectedFunds > div:hover {
            transform: scale(1.02);
            box-shadow: 0 8px 24px var(--shadow-alpha);
        }
        
        /* Tooltips & Modals */
        #pgSearchResults {
            animation: slideDown 0.3s cubic-bezier(0.1, 0.7, 0.1, 1) forwards;
            transform-origin: top center;
        }
        @keyframes slideDown {
            from { opacity: 0; transform: translateY(-10px) scaleY(0.95); }
            to { opacity: 1; transform: translateY(0) scaleY(1); }
        }
        
        /* Smooth Range Sliders */
        input[type="range"] {
            transition: opacity 0.2s;
        }
        input[type="range"]::-webkit-slider-thumb {
            transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        input[type="range"]::-webkit-slider-thumb:hover {
            transform: scale(1.3);
        }
"""
    # Check if we already injected it so we don't duplicate
    if "Premium Smooth Animations" not in content:
        # Inject right before </style>
        content = content.replace('</style>', premium_css + '\n    </style>')
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Premium smooth animations successfully injected!")
    else:
        print("Smooth animations are already installed.")

if __name__ == '__main__':
    add_smooth_animations()
