/**
 * ProMutualFund Analytics - Global Internationalization (i18n) Engine
 * Supports 3 Languages: English (en), मराठी (mr), हिंदी (hi)
 * Seamlessly translates entire website: Dashboard, News, Verifier, and Login pages.
 */

(function () {
  'use strict';

  const STORAGE_KEY = 'site_lang';
  const NEWS_STORAGE_KEY = 'news_lang';

  const I18N_DICTIONARY = {
    // ── GLOBAL & NAVIGATION ──
    "ProMutualFund": { en: "ProMutualFund", mr: "प्रोम्युच्युअल फंड", hi: "प्रोम्यूचुअल फंड" },
    "TERMINAL": { en: "TERMINAL", mr: "टर्मिनल", hi: "टर्मिनल" },
    "Institutional Analytics Terminal": { en: "Institutional Analytics Terminal", mr: "संस्थात्मक विश्लेषणात्मक टर्मिनल", hi: "संस्थागत विश्लेषणात्मक टर्मिनल" },
    "Live AMFI": { en: "Live AMFI", mr: "थेट AMFI डेटा", hi: "लाइव AMFI डेटा" },
    "REFRESH": { en: "REFRESH", mr: "रिफ्रेश", hi: "रिफ्रेश" },
    "SAVED": { en: "SAVED", mr: "जतन केलेले", hi: "सहेजे गए" },
    "NEWS": { en: "NEWS", mr: "बातम्या", hi: "समाचार" },
    "VERIFY": { en: "VERIFY", mr: "पडताळणी", hi: "सत्यापित" },
    "CREATE PORTFOLIO": { en: "CREATE PORTFOLIO", mr: "पोर्टफोलिओ तयार करा", hi: "पोर्टफोलियो बनाएं" },
    "LOGOUT": { en: "LOGOUT", mr: "लॉगआउट", hi: "लॉगआउट" },
    "Return to Dashboard": { en: "Return to Dashboard", mr: "डॅशबोर्डवर परत जा", hi: "डैशबोर्ड पर वापस जाएं" },
    "← Back to Dashboard": { en: "← Back to Dashboard", mr: "← डॅशबोर्डवर परत जा", hi: "← डैशबोर्ड पर वापस जाएं" },
    "Back to Dashboard": { en: "Back to Dashboard", mr: "डॅशबोर्डवर परत जा", hi: "डैशबोर्ड पर वापस जाएं" },

    // ── SEARCH & FILTERS ──
    "Search 14,000+ mutual funds...": { en: "Search 14,000+ mutual funds...", mr: "१४,०००+ म्युच्युअल फंड शोधा...", hi: "14,000+ म्यूचुअल फंड खोजें..." },
    "Search funds, AMCs or schemes...": { en: "Search funds, AMCs or schemes...", mr: "फंड, AMC किंवा योजना शोधा...", hi: "फंड, AMC या योजना खोजें..." },
    "Search financial news, SEBI regulations, cities or keywords...": { en: "Search financial news, SEBI regulations, cities or keywords...", mr: "आर्थिक घडामोडी, सेबी नियम, शहरे किंवा शब्द शोधा...", hi: "वित्तीय समाचार, सेबी नियम, शहर या कीवर्ड खोजें..." },
    "All": { en: "All", mr: "सर्व (All)", hi: "सभी (All)" },
    "🔥 Equity": { en: "🔥 Equity", mr: "🔥 इक्विटी (Equity)", hi: "🔥 इक्विटी (Equity)" },
    "⚖️ Hybrid": { en: "⚖️ Hybrid", mr: "⚖️ हायब्रिड (Hybrid)", hi: "⚖️ हाइब्रिड (Hybrid)" },
    "📈 Index": { en: "📈 Index", mr: "📈 इंडेक्स (Index)", hi: "📈 इंडेक्स (Index)" },
    "🛡️ Debt": { en: "🛡️ Debt", mr: "🛡️ डेट (Debt)", hi: "🛡️ डेट (Debt)" },
    "💧 Liquid": { en: "💧 Liquid", mr: "💧 लिक्विड (Liquid)", hi: "💧 लिक्विड (Liquid)" },
    "🥇 Gold": { en: "🥇 Gold", mr: "🥇 सुवर्ण (Gold)", hi: "🥇 स्वर्ण (Gold)" },
    "📊 ETF": { en: "📊 ETF", mr: "📊 ईटीएफ (ETF)", hi: "📊 ईटीएफ (ETF)" },
    "🌐 Multi Asset": { en: "🌐 Multi Asset", mr: "🌐 मल्टी ॲसेट", hi: "🌐 मल्टी एसेट" },

    // ── MARQUEE BADGES ──
    "TOP RETURN": { en: "TOP RETURN", mr: "उत्कृष्ट परतावा", hi: "शीर्ष रिटर्न" },
    "BALANCED": { en: "BALANCED", mr: "संतुलित", hi: "संतुलित" },
    "TRENDING": { en: "TRENDING", mr: "ट्रेंडिंग", hi: "ट्रेंडिंग" },
    "POPULAR": { en: "POPULAR", mr: "लोकप्रिय", hi: "लोकप्रिय" },
    "CONSISTENT": { en: "CONSISTENT", mr: "सातत्यपूर्ण", hi: "सुसंगत" },
    "STABILITY": { en: "STABILITY", mr: "स्थैर्य", hi: "स्थिरता" },

    // ── DASHBOARD & METRICS ──
    "MARKET PULSE": { en: "MARKET PULSE", mr: "बाजार नाडी (पल्स)", hi: "बाजार नब्ज (पल्स)" },
    "PORTFOLIO OVERVIEW": { en: "PORTFOLIO OVERVIEW", mr: "पोर्टफोलिओ आढावा", hi: "पोर्टफोलियो अवलोकन" },
    "FUND COMPARISON": { en: "FUND COMPARISON", mr: "फंड तुलना", hi: "फंड तुलना" },
    "SIP CALCULATOR": { en: "SIP CALCULATOR", mr: "एसआयपी कॅल्क्युलेटर", hi: "एसआईपी कैलकुलेटर" },
    "RISK METRICS": { en: "RISK METRICS", mr: "जोखीम विश्लेषण", hi: "जोखिम विश्लेषण" },
    "LIVE TICKER": { en: "LIVE TICKER", mr: "थेट टिकर", hi: "लाइव टिकर" },
    "BREAKING WIRE": { en: "BREAKING WIRE", mr: "ताजी बातमी", hi: "ताज़ा खबर" },
    "MONTHLY SIP INFLOW": { en: "MONTHLY SIP INFLOW", mr: "मासिक एसआयपी प्रवाह", hi: "मासिक एसआईपी प्रवाह" },
    "TOTAL MF AUM": { en: "TOTAL MF AUM", mr: "एकूण म्युच्युअल फंड AUM", hi: "कुल म्यूचुअल फंड AUM" },
    "10Y G-SEC": { en: "10Y G-SEC", mr: "१०-वर्षीय सरकारी रोखे", hi: "10-वर्षीय सरकारी बॉन्ड" },
    "MCX GOLD (10g)": { en: "MCX GOLD (10g)", mr: "MCX सोने (१० ग्रॅम)", hi: "MCX सोना (10 ग्राम)" },
    "RECORD ATH": { en: "RECORD ATH", mr: "सर्वोच्च उच्चांक", hi: "सर्वकालिक उच्च स्तर" },

    // ── VERIFIER PAGE ──
    "Portfolio Multi-Fund Audit": { en: "Portfolio Multi-Fund Audit", mr: "पोर्टफोलिओ मल्टि-फंड ऑडिट", hi: "पोर्टफोलियो मल्टी-फंड ऑडिट" },
    "Simultaneous Verification": { en: "Simultaneous Verification", mr: "एकाच वेळी पडताळणी", hi: "एक साथ सत्यापन" },
    "Portfolio Verification": { en: "Portfolio Verification", mr: "पोर्टफोलिओ पडताळणी", hi: "पोर्टफोलियो सत्यापन" },
    "Re-Verify All Funds": { en: "Re-Verify All Funds", mr: "सर्व फंड पुन्हा पडताळा", hi: "सभी फंड पुनः सत्यापित करें" },
    "AMFI Official Feed Active": { en: "AMFI Official Feed Active", mr: "अधिकृत AMFI फीड सक्रिय", hi: "आधिकारिक AMFI फीड सक्रिय" },
    "Audit Mutual Fund Scheme": { en: "Audit Mutual Fund Scheme", mr: "म्युच्युअल फंड योजना ऑडिट करा", hi: "म्यूचुअल फंड स्कीम ऑडिट करें" },
    "Verified against official AMFI registry": { en: "Verified against official AMFI registry", mr: "अधिकृत AMFI नोंदणीनुसार पडताळणी", hi: "आधिकारिक AMFI रजिस्ट्री से सत्यापित" },
    "Schemes Audited": { en: "Schemes Audited", mr: "योजना ऑडिट झाल्या", hi: "स्कीमें ऑडिट की गईं" },
    "Tolerance Threshold": { en: "Tolerance Threshold", mr: "सहनशीलता मर्यादा", hi: "सहनशीलता सीमा" },

    // ── LOGIN PAGE ──
    "Partner ID": { en: "Partner ID", mr: "पार्टनर आयडी (Partner ID)", hi: "पार्टनर आईडी (Partner ID)" },
    "Password": { en: "Password", mr: "पासवर्ड (Password)", hi: "पासवर्ड (Password)" },
    "Enter Captcha": { en: "Enter Captcha", mr: "कॅप्चा टाका", hi: "कैप्चा दर्ज करें" },
    "Enter your password": { en: "Enter your password", mr: "तुमचा पासवर्ड टाका", hi: "अपना पासवर्ड दर्ज करें" },
    "INSTITUTIONAL GRADE PORTFOLIO BUILDER": { en: "INSTITUTIONAL GRADE PORTFOLIO BUILDER", mr: "संस्थात्मक दर्जाचा पोर्टफोलिओ बिल्डर", hi: "संस्थागत ग्रेड पोर्टफोलियो बिल्डर" },
    "SECURE LOGIN": { en: "SECURE LOGIN", mr: "सुरक्षित लॉगिन करा", hi: "सुरक्षित लॉगिन करें" },
    "Institutional Terminal Login": { en: "Institutional Terminal Login", mr: "संस्थात्मक टर्मिनल लॉगिन", hi: "संस्थागत टर्मिनल लॉगिन" },

    // ── NEWS PAGE MODES & CONTROLS ──
    "FINANCIAL MARKETS": { en: "FINANCIAL MARKETS", mr: "वित्तीय व भांडवली बाजार", hi: "वित्तीय व पूंजी बाजार" },
    "REGULAR NEWS / AREA LOCAL": { en: "REGULAR NEWS / AREA LOCAL", mr: "स्थानिक व परिसर बातम्या (चंद्रपूर विशेष)", hi: "स्थानीय व क्षेत्रीय समाचार (चंद्रपुर विशेष)" },
    "SELECT METRO / AREA FOCUS": { en: "SELECT METRO / AREA FOCUS", mr: "शहर / परिसर निवडा", hi: "शहर / क्षेत्र चुनें" },
    "Chandrapur (MH)": { en: "Chandrapur (MH)", mr: "चंद्रपूर (महाराष्ट्र)", hi: "चंद्रपुर (महाराष्ट्र)" },
    "CHANDRAPUR & VIDARBHA LOCAL WIRE (LOKMAT)": { en: "CHANDRAPUR & VIDARBHA LOCAL WIRE (LOKMAT)", mr: "चंद्रपूर व विदर्भ स्थानिक बातमीपत्र (लोकमत)", hi: "चंद्रपुर व विदर्भ स्थानीय समाचार पत्र (लोकमत)" },
    "Continuous Local Field Wire • Chandrapur Municipal Corporation, Tadoba & District Authorities": { en: "Continuous Local Field Wire • Chandrapur Municipal Corporation, Tadoba & District Authorities", mr: "थेट स्थानिक वार्तांकन • चंद्रपूर महानगरपालिका, ताडोबा व जिल्हा प्रशासन", hi: "सीधा स्थानीय कवरेज • चंद्रपुर नगर निगम, ताडोबा व जिला प्रशासन" },
    "ALL EDITIONS": { en: "ALL EDITIONS", mr: "सर्व आवृत्त्या", hi: "सभी संस्करण" },
    "CIVIC & MUNICIPAL": { en: "CIVIC & MUNICIPAL", mr: "नागरी कामे व मनपा", hi: "नागरिक विकास व नगर निगम" },
    "TADOBA & WILDLIFE": { en: "TADOBA & WILDLIFE", mr: "ताडोबा व वन्यजीव", hi: "ताडोबा व वन्यजीव" },
    "ROADS & TRANSIT": { en: "ROADS & TRANSIT", mr: "रस्ते व वाहतूक", hi: "सड़कें व यातायात" },
    "WEATHER & AQI": { en: "WEATHER & AQI", mr: "हवामान व प्रदूषण", hi: "मौसम व प्रदूषण" },
    "POLICE & SAFETY": { en: "POLICE & SAFETY", mr: "पोलीस व सुरक्षा", hi: "पुलिस व सुरक्षा" }
  };

  // Language state
  let currentLang = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(NEWS_STORAGE_KEY) || 'en';

  function getLang() {
    return currentLang;
  }

  function t(key) {
    if (!key) return '';
    const trimmed = key.trim();
    if (I18N_DICTIONARY[trimmed] && I18N_DICTIONARY[trimmed][currentLang]) {
      return I18N_DICTIONARY[trimmed][currentLang];
    }
    return key;
  }

  function setLanguage(lang) {
    if (!['en', 'mr', 'hi'].includes(lang)) lang = 'en';
    currentLang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
    localStorage.setItem(NEWS_STORAGE_KEY, lang);

    // Update lang badge in HTML
    document.documentElement.lang = lang === 'mr' ? 'mr' : (lang === 'hi' ? 'hi' : 'en');

    // Update Dropdown Buttons
    updateSelectorUI(lang);

    // Apply translations across all DOM text nodes and attributes
    translatePage(lang);

    // Dispatch custom event for page scripts (e.g. news.html or index.html)
    window.dispatchEvent(new CustomEvent('siteLanguageChanged', { detail: { lang } }));
  }

  function updateSelectorUI(lang) {
    const labelMap = { en: 'English', mr: 'मराठी', hi: 'हिंदी' };
    const label = labelMap[lang] || 'English';

    // Update any label span
    const labels = document.querySelectorAll('.site-current-lang-text, #siteCurrentLangLabel, #currentLangLabel');
    labels.forEach(el => { el.textContent = label; });

    // Update active class on dropdown items
    document.querySelectorAll('.lang-option-btn, .site-lang-opt').forEach(btn => {
      const optLang = btn.getAttribute('data-lang') || (btn.id ? btn.id.replace('langOpt_', '') : '');
      const checkIcon = btn.querySelector('.lang-check');
      if (optLang === lang) {
        btn.classList.add('active');
        if (checkIcon) checkIcon.style.display = 'inline-block';
      } else {
        btn.classList.remove('active');
        if (checkIcon) checkIcon.style.display = 'none';
      }
    });
  }

  function translatePage(lang) {
    // 1. Elements with explicit data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (I18N_DICTIONARY[key] && I18N_DICTIONARY[key][lang]) {
        el.textContent = I18N_DICTIONARY[key][lang];
      }
    });

    // 2. Elements with data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (I18N_DICTIONARY[key] && I18N_DICTIONARY[key][lang]) {
        el.placeholder = I18N_DICTIONARY[key][lang];
      }
    });

    // 3. Elements with data-i18n-title
    document.querySelectorAll('[data-i18n-title]').forEach(el => {
      const key = el.getAttribute('data-i18n-title');
      if (I18N_DICTIONARY[key] && I18N_DICTIONARY[key][lang]) {
        el.title = I18N_DICTIONARY[key][lang];
      }
    });

    // 4. Targeted known UI elements across pages
    // Search inputs
    const searchInputs = document.querySelectorAll('#searchInput, .search-input');
    searchInputs.forEach(inp => {
      if (lang === 'mr') inp.placeholder = '१४,०००+ म्युच्युअल फंड शोधा...';
      else if (lang === 'hi') inp.placeholder = '14,000+ म्यूचुअल फंड खोजें...';
      else inp.placeholder = 'Search 14,000+ mutual funds...';
    });

    const newsSearch = document.getElementById('newsSearchInput');
    if (newsSearch) {
      if (lang === 'mr') newsSearch.placeholder = 'आर्थिक घडामोडी, सेबी नियम, शहरे (उदा. चंद्रपूर) किंवा शब्द शोधा...';
      else if (lang === 'hi') newsSearch.placeholder = 'वित्तीय समाचार, सेबी नियम, शहर (उदा. चंद्रपुर) या कीवर्ड खोजें...';
      else newsSearch.placeholder = 'Search financial news, SEBI regulations, cities (e.g. Chandrapur)...';
    }

    // Header buttons in index.html
    const btnItems = document.querySelectorAll('.btn-header-item');
    btnItems.forEach(b => {
      const text = b.textContent.trim();
      if (text.includes('REFRESH') || text.includes('रिफ्रेश')) {
        b.innerHTML = `<span>🔄</span> ${lang === 'mr' ? 'रिफ्रेश' : (lang === 'hi' ? 'रिफ्रेश' : 'REFRESH')}`;
      } else if (text.includes('SAVED') || text.includes('जतन') || text.includes('सहेजे')) {
        b.innerHTML = `<span>📁</span> ${lang === 'mr' ? 'जतन केलेले' : (lang === 'hi' ? 'सहेजे गए' : 'SAVED')}`;
      } else if (text.includes('NEWS') || text.includes('बातम्या') || text.includes('समाचार')) {
        b.innerHTML = `<span>📰</span> ${lang === 'mr' ? 'बातम्या' : (lang === 'hi' ? 'समाचार' : 'NEWS')}`;
      } else if (text.includes('VERIFY') || text.includes('पडताळणी') || text.includes('सत्यापित')) {
        b.innerHTML = `<span>🛡️</span> ${lang === 'mr' ? 'पडताळणी' : (lang === 'hi' ? 'सत्यापित' : 'VERIFY')}`;
      }
    });

    // Create portfolio button
    const btnCreate = document.querySelector('.btn-create-portfolio');
    if (btnCreate) {
      btnCreate.innerHTML = `<span>⚡</span> ${lang === 'mr' ? 'पोर्टफोलिओ तयार करा' : (lang === 'hi' ? 'पोर्टफोलियो बनाएं' : 'CREATE PORTFOLIO')}`;
    }

    // Logout button
    const btnLogout = document.querySelector('.btn-logout');
    if (btnLogout) {
      btnLogout.innerHTML = `<span>🚪</span> ${lang === 'mr' ? 'लॉगआउट' : (lang === 'hi' ? 'लॉगआउट' : 'LOGOUT')}`;
    }

    // Live AMFI badge
    const liveAmfi = document.querySelector('.live-badge .live-text');
    if (liveAmfi) {
      liveAmfi.textContent = lang === 'mr' ? 'थेट AMFI' : (lang === 'hi' ? 'लाइव AMFI' : 'Live AMFI');
    }

    // Subtitle tagline
    const headerSub = document.querySelector('.header-brand-wrap p');
    if (headerSub) {
      headerSub.textContent = lang === 'mr' ? 'संस्थात्मक विश्लेषणात्मक टर्मिनल' : (lang === 'hi' ? 'संस्थागत विश्लेषणात्मक टर्मिनल' : 'Institutional Analytics Terminal');
    }

    // Back to dashboard buttons
    const backBtn = document.getElementById('backToDashBtn') || document.querySelector('button[onclick*="location=\'/dashboard\'"]');
    if (backBtn) {
      const textSpan = backBtn.querySelector('#backToDashText') || backBtn;
      if (textSpan) {
        if (textSpan.id === 'backToDashText') {
          textSpan.textContent = lang === 'mr' ? 'डॅशबोर्डवर परत जा' : (lang === 'hi' ? 'डैशबोर्ड पर वापस जाएं' : 'Return to Dashboard');
        } else {
          backBtn.innerHTML = `← ${lang === 'mr' ? 'डॅशबोर्डवर परत जा' : (lang === 'hi' ? 'डैशबोर्ड पर वापस जाएं' : 'Back to Dashboard')}`;
        }
      }
    }

    // Quick filter chips in index.html
    const chipMap = {
      'All': { mr: 'सर्व (All)', hi: 'सभी (All)', en: 'All' },
      'Equity': { mr: '🔥 इक्विटी', hi: '🔥 इक्विटी', en: '🔥 Equity' },
      'Hybrid / Balanced': { mr: '⚖️ हायब्रिड', hi: '⚖️ हाइब्रिड', en: '⚖️ Hybrid' },
      'Index': { mr: '📈 इंडेक्स', hi: '📈 इंडेक्स', en: '📈 Index' },
      'Debt': { mr: '🛡️ डेट', hi: '🛡️ डेट', en: '🛡️ Debt' },
      'Liquid': { mr: '💧 लिक्विड', hi: '💧 लिक्विड', en: '💧 Liquid' },
      'Gold': { mr: '🥇 सुवर्ण', hi: '🥇 स्वर्ण', en: '🥇 Gold' },
      'ETF': { mr: '📊 ईटीएफ', hi: '📊 ईटीएफ', en: '📊 ETF' },
      'Multi Asset': { mr: '🌐 मल्टी ॲसेट', hi: '🌐 मल्टी एसेट', en: '🌐 Multi Asset' }
    };
    document.querySelectorAll('.q-chip').forEach(ch => {
      const cat = ch.getAttribute('data-cat');
      if (cat && chipMap[cat]) {
        ch.textContent = chipMap[cat][lang] || chipMap[cat]['en'];
      }
    });

    // Login form elements if present
    const partnerLabel = document.querySelector('label[for="partnerId"]');
    if (partnerLabel) partnerLabel.textContent = lang === 'mr' ? 'पार्टनर आयडी (Partner ID)' : (lang === 'hi' ? 'पार्टनर आईडी (Partner ID)' : 'Partner ID');
    const pwdLabel = document.querySelector('label[for="password"]');
    if (pwdLabel) pwdLabel.textContent = lang === 'mr' ? 'पासवर्ड (Password)' : (lang === 'hi' ? 'पासवर्ड (Password)' : 'Password');
    const pwdInput = document.getElementById('password');
    if (pwdInput) pwdInput.placeholder = lang === 'mr' ? 'तुमचा पासवर्ड टाका' : (lang === 'hi' ? 'अपना पासवर्ड दर्ज करें' : 'Enter your password');
    const captchaInput = document.getElementById('captchaInput');
    if (captchaInput) captchaInput.placeholder = lang === 'mr' ? 'कॅप्चा टाका' : (lang === 'hi' ? 'कैप्चा दर्ज करें' : 'Enter Captcha');
    const loginBtn = document.getElementById('loginBtn');
    if (loginBtn) {
      const span = loginBtn.querySelector('span');
      if (span) span.textContent = lang === 'mr' ? 'सुरक्षित लॉगिन' : (lang === 'hi' ? 'सुरक्षित लॉगिन' : 'SECURE LOGIN');
    }
  }

  // Render language switcher dropdown component dynamically if not present
  function injectLanguageSelector(targetSelector, customStyles) {
    const target = document.querySelector(targetSelector);
    if (!target || target.querySelector('#siteLanguageDropdownContainer')) return;

    const container = document.createElement('div');
    container.id = 'siteLanguageDropdownContainer';
    container.className = 'site-lang-selector-wrap';
    container.style.cssText = customStyles || 'position: relative; display: inline-flex; align-items: center; z-index: 100;';

    const langLabel = { en: 'English', mr: 'मराठी', hi: 'हिंदी' }[currentLang] || 'English';

    container.innerHTML = `
      <button type="button" id="siteBtnLangDropdown" onclick="window.toggleSiteLanguageMenu(event)"
        style="background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); border-radius: 8px; color: #F1F5F9; padding: 6px 12px; font-size: 11px; font-weight: 700; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; transition: all 150ms;"
        title="Translate Website (Hindi, English, Marathi)">
        <span style="font-size: 13px;">🌐</span>
        <span class="site-current-lang-text" id="siteCurrentLangLabel">${langLabel}</span>
        <span style="font-size: 8px; color: #94A3B8;">▼</span>
      </button>
      <div id="siteLanguageDropdownMenu" style="display: none; position: absolute; right: 0; top: calc(100% + 6px); background: #0D1B2A; border: 1px solid rgba(56,189,248,0.25); border-radius: 12px; padding: 6px; min-width: 170px; box-shadow: 0 10px 30px rgba(0,0,0,0.6); z-index: 9999;">
        <div style="font-size: 9px; font-weight: 800; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em; padding: 4px 8px 6px;">SELECT LANGUAGE</div>
        <button type="button" onclick="window.setSiteLanguage('en')" class="site-lang-opt lang-option-btn ${currentLang === 'en' ? 'active' : ''}" data-lang="en" style="width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 7px 10px; border-radius: 6px; background: transparent; border: none; color: #E2E8F0; font-size: 11px; font-weight: 700; cursor: pointer; text-align: left;">
          <span>🇬🇧 English</span>
          <span class="lang-check" style="font-size: 11px; color: #38BDF8; ${currentLang === 'en' ? '' : 'display: none;'}">✓</span>
        </button>
        <button type="button" onclick="window.setSiteLanguage('mr')" class="site-lang-opt lang-option-btn ${currentLang === 'mr' ? 'active' : ''}" data-lang="mr" style="width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 7px 10px; border-radius: 6px; background: transparent; border: none; color: #E2E8F0; font-size: 11px; font-weight: 700; cursor: pointer; text-align: left; margin-top: 2px;">
          <span>🇮🇳 मराठी (Marathi)</span>
          <span class="lang-check" style="font-size: 11px; color: #38BDF8; ${currentLang === 'mr' ? '' : 'display: none;'}">✓</span>
        </button>
        <button type="button" onclick="window.setSiteLanguage('hi')" class="site-lang-opt lang-option-btn ${currentLang === 'hi' ? 'active' : ''}" data-lang="hi" style="width: 100%; display: flex; align-items: center; justify-content: space-between; padding: 7px 10px; border-radius: 6px; background: transparent; border: none; color: #E2E8F0; font-size: 11px; font-weight: 700; cursor: pointer; text-align: left; margin-top: 2px;">
          <span>🇮🇳 हिंदी (Hindi)</span>
          <span class="lang-check" style="font-size: 11px; color: #38BDF8; ${currentLang === 'hi' ? '' : 'display: none;'}">✓</span>
        </button>
      </div>
    `;

    target.appendChild(container);
  }

  // Toggle Dropdown Menu
  window.toggleSiteLanguageMenu = function (e) {
    if (e) e.stopPropagation();
    const menu = document.getElementById('siteLanguageDropdownMenu') || document.getElementById('languageDropdownMenu');
    if (menu) {
      menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
  };

  // Click outside to dismiss dropdown
  document.addEventListener('click', function (e) {
    const wrap = document.getElementById('siteLanguageDropdownContainer') || document.getElementById('languageSelectorContainer');
    const menu = document.getElementById('siteLanguageDropdownMenu') || document.getElementById('languageDropdownMenu');
    if (menu && wrap && !wrap.contains(e.target)) {
      menu.style.display = 'none';
    }
  });

  // Export functions to window
  window.ProI18n = {
    getLang,
    t,
    setLanguage,
    translatePage,
    injectLanguageSelector
  };
  window.setSiteLanguage = setLanguage;

  // Auto-run on DOM ready
  document.addEventListener('DOMContentLoaded', function () {
    const saved = localStorage.getItem(STORAGE_KEY) || localStorage.getItem(NEWS_STORAGE_KEY) || 'en';
    setLanguage(saved);
  });

})();
