/**
 * ══════════════════════════════════════════════════════════════════════════
 * ProMutualFund Analytics - Real-Time Streaming & WebSocket Client Engine
 * High-performance bidirectional streaming controller for market ticks,
 * sentiment indexes, and background AMFI synchronization.
 * ══════════════════════════════════════════════════════════════════════════
 */

(function () {
  'use strict';

  // Global diagnostics state
  window.MF_WS_STATE = {
    connected: false,
    socketId: null,
    latencyMs: 0,
    packetsReceived: 0,
    connectedClients: 1,
    connectedSince: null,
    lastTickTime: null,
    activeTransport: 'polling'
  };

  // Ensure socket is available
  if (typeof io === 'undefined') {
    console.warn('[MF WebSocket] Socket.IO client library not detected. Real-time stream disabled.');
    return;
  }

  // Reuse existing socket instance or create one
  const socket = window.socket || io({
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1000,
    reconnectionDelayMax: 5000,
    timeout: 10000,
    transports: ['websocket', 'polling']
  });
  window.socket = socket;

  let pingIntervalTimer = null;

  // ──────────────────────────────────────────────────────────────────────────
  // 1. CONNECTION LIFECYCLE HANDLERS
  // ──────────────────────────────────────────────────────────────────────────

  socket.on('connect', () => {
    window.MF_WS_STATE.connected = true;
    window.MF_WS_STATE.socketId = socket.id;
    window.MF_WS_STATE.connectedSince = new Date();
    window.MF_WS_STATE.activeTransport = socket.io.engine ? socket.io.engine.transport.name : 'websocket';

    console.log(`%c[MF WebSocket] 🟢 Live Stream Connected. Transport: ${window.MF_WS_STATE.activeTransport} (ID: ${socket.id})`, 'color: #10B981; font-weight: bold;');

    updateBadgeStatus(true, 'WS LIVE');
    startLatencyPing();

    // Trigger initial requests
    socket.emit('request_market_tick');
    socket.emit('request_market_mood');
  });

  socket.on('disconnect', (reason) => {
    window.MF_WS_STATE.connected = false;
    console.warn('[MF WebSocket] 🔴 Stream disconnected:', reason);
    updateBadgeStatus(false, 'RECONNECTING...');
    clearInterval(pingIntervalTimer);
  });

  socket.on('connect_error', (err) => {
    console.warn('[MF WebSocket] Connection error:', err.message);
    updateBadgeStatus(false, 'CONNECT ERROR');
  });

  socket.on('ws_connected', (data) => {
    if (data) {
      window.MF_WS_STATE.connectedClients = data.clients_count || 1;
      updateDiagnosticsUI();
    }
  });

  // ──────────────────────────────────────────────────────────────────────────
  // 2. LATENCY PING ENGINE
  // ──────────────────────────────────────────────────────────────────────────

  function startLatencyPing() {
    clearInterval(pingIntervalTimer);
    sendPing();
    pingIntervalTimer = setInterval(sendPing, 4000);
  }

  function sendPing() {
    if (!socket.connected) return;
    const clientTimestamp = Date.now();
    socket.emit('ping_check', { client_timestamp: clientTimestamp });
  }

  socket.on('pong_check', (data) => {
    if (data && data.client_timestamp) {
      const now = Date.now();
      const rtt = Math.max(1, Math.round(now - data.client_timestamp));
      window.MF_WS_STATE.latencyMs = rtt;
      if (data.clients_count) {
        window.MF_WS_STATE.connectedClients = data.clients_count;
      }

      const pingEl = document.getElementById('wsStreamPing');
      if (pingEl) {
        pingEl.textContent = `${rtt}ms`;
        if (rtt < 100) {
          pingEl.style.color = '#34D399';
        } else if (rtt < 300) {
          pingEl.style.color = '#F59E0B';
        } else {
          pingEl.style.color = '#F87171';
        }
      }
      updateDiagnosticsUI();
    }
  });

  // ──────────────────────────────────────────────────────────────────────────
  // 3. REAL-TIME MARKET TICK STREAM HANDLER
  // ──────────────────────────────────────────────────────────────────────────

  socket.on('market_tick', (payload) => {
    if (!payload) return;
    window.MF_WS_STATE.packetsReceived++;
    window.MF_WS_STATE.lastTickTime = payload.timestamp || new Date().toLocaleTimeString();

    applyMarketTick(payload);
    updateDiagnosticsUI();
  });

  function applyMarketTick(data) {
    // 1. Dashboard Ticker Ribbon
    updateIndexElement('dashNiftyVal', 'dashNiftyChg', data.nifty);
    updateIndexElement('dashSensexVal', 'dashSensexChg', data.sensex);
    updateIndexElement('dashVixVal', 'dashVixChg', data.vix);

    if (data.sip_inflow) {
      const sipVal = document.getElementById('dashSipVal') || document.getElementById('tickerSipVal');
      if (sipVal && data.sip_inflow.value) sipVal.textContent = data.sip_inflow.value;
      const sipBadge = document.getElementById('tickerSipBadge');
      if (sipBadge && data.sip_inflow.badge) sipBadge.textContent = data.sip_inflow.badge;
    }
    if (data.total_aum) {
      const aumVal = document.getElementById('dashAumVal') || document.getElementById('tickerAumVal');
      const aumChg = document.getElementById('dashAumChg') || document.getElementById('tickerAumChg');
      if (aumVal && data.total_aum.value) aumVal.textContent = data.total_aum.value;
      if (aumChg && data.total_aum.change) aumChg.textContent = data.total_aum.change;
    }
    if (data.gsec_10y) {
      const gsecVal = document.getElementById('dashGsecVal') || document.getElementById('tickerGsecVal');
      const gsecChg = document.getElementById('dashGsecChg') || document.getElementById('tickerGsecChg');
      if (gsecVal && data.gsec_10y.value) gsecVal.textContent = data.gsec_10y.value;
      if (gsecChg && data.gsec_10y.change) gsecChg.textContent = data.gsec_10y.change;
    }
    if (data.gold_10g) {
      const goldVal = document.getElementById('dashGoldVal') || document.getElementById('tickerGoldVal');
      const goldChg = document.getElementById('dashGoldChg') || document.getElementById('tickerGoldChg');
      if (goldVal && data.gold_10g.value) goldVal.textContent = data.gold_10g.value;
      if (goldChg && data.gold_10g.change) goldChg.textContent = data.gold_10g.change;
    }

    const lastTickEl = document.getElementById('dashLastTickTime') || document.getElementById('tickerLastTickTime');
    if (lastTickEl && data.timestamp) {
      lastTickEl.textContent = data.timestamp;
    }

    // 2. Also sync dedicated newsroom ticker if present
    updateIndexElement('tickerNiftyVal', 'tickerNiftyChg', data.nifty);
    updateIndexElement('tickerSensexVal', 'tickerSensexChg', data.sensex);
    updateIndexElement('tickerVixVal', 'tickerVixChg', data.vix);
    updateIndexElement('tickerGoldVal', 'tickerGoldChg', data.gold_10g);
    updateIndexElement('tickerGsecVal', 'tickerGsecChg', data.gsec_10y);

    // 3. Sync Spot Nifty & VIX in Market Mood Card if visible
    if (data.nifty && data.nifty.raw_price) {
      const fpNifty = document.getElementById('fpNiftySpotVal');
      if (fpNifty) fpNifty.textContent = Math.round(data.nifty.raw_price).toLocaleString('en-IN');
    }
    if (data.vix && data.vix.raw_price) {
      const fpVix = document.getElementById('fpIndiaVixVal');
      if (fpVix) fpVix.textContent = data.vix.raw_price.toFixed(2);
    }
  }

  function updateIndexElement(valId, chgId, indexObj) {
    if (!indexObj) return;

    const valEl = document.getElementById(valId);
    const chgEl = document.getElementById(chgId);

    if (valEl && indexObj.price) {
      const oldVal = valEl.textContent;
      valEl.textContent = indexObj.price;

      // Trigger flash animation on value change
      if (oldVal && oldVal !== indexObj.price && oldVal !== '--') {
        const flashClass = indexObj.tick === 'down' ? 'tick-flash-red' : 'tick-flash-green';
        valEl.classList.remove('tick-flash-green', 'tick-flash-red');
        void valEl.offsetWidth; // Force CSS reflow
        valEl.classList.add(flashClass);
        setTimeout(() => valEl.classList.remove(flashClass), 900);
      }
    }

    if (chgEl && indexObj.change) {
      chgEl.textContent = indexObj.change;
      if (indexObj.direction === 'up') {
        chgEl.style.color = '#34D399';
      } else if (indexObj.direction === 'down') {
        chgEl.style.color = '#F87171';
      }
    }
  }

  // ──────────────────────────────────────────────────────────────────────────
  // 4. REAL-TIME MARKET MOOD (MMI) UPDATE HANDLER
  // ──────────────────────────────────────────────────────────────────────────

  socket.on('market_mood_update', (mood) => {
    if (!mood) return;

    // Update MMI score
    const mmiValEl = document.getElementById('fpMmiScoreVal');
    if (mmiValEl && mood.mmi_val !== undefined) {
      mmiValEl.textContent = mood.mmi_val;
    }

    // Update Needle position smoothly
    const needleEl = document.getElementById('fpMoodNeedle');
    if (needleEl && mood.mmi_val !== undefined) {
      const clampedVal = Math.max(0, Math.min(100, mood.mmi_val));
      needleEl.style.left = `${clampedVal}%`;
    }

    // Update Advice Narrative
    const adviceEl = document.getElementById('fpMoodAdviceText');
    if (adviceEl && mood.mmi_desc) {
      adviceEl.textContent = mood.mmi_desc;
    }

    // Update Lump Sum / STP recommendation badges
    const lumpActionEl = document.getElementById('fpLumpAction');
    const lumpDescEl = document.getElementById('fpLumpDesc');
    const lumpBadgeEl = document.getElementById('fpLumpBadge');

    if (lumpActionEl && mood.lump_action) lumpActionEl.textContent = mood.lump_action;
    if (lumpDescEl && mood.lump_desc) lumpDescEl.textContent = mood.lump_desc;
    if (lumpBadgeEl && mood.zone) lumpBadgeEl.textContent = mood.zone;

    // PE / FII Flow
    const peEl = document.getElementById('fpNiftyPeVal');
    if (peEl && mood.nifty_pe) peEl.textContent = mood.nifty_pe;

    const fiiEl = document.getElementById('fpFiiFlowVal');
    if (fiiEl && mood.fii_flow !== undefined) {
      const prefix = mood.fii_flow >= 0 ? '+₹' : '-₹';
      fiiEl.textContent = `${prefix}${Math.abs(mood.fii_flow).toLocaleString('en-IN')} Cr`;
      fiiEl.style.color = mood.fii_flow >= 0 ? '#34D399' : '#F87171';
    }
  });

  // ──────────────────────────────────────────────────────────────────────────
  // 5. AMFI DAILY BACKGROUND SYNC & NOTIFICATION TOASTS
  // ──────────────────────────────────────────────────────────────────────────

  socket.on('amfi_sync_update', (evt) => {
    if (!evt) return;

    if (evt.status === 'success') {
      showToast({
        title: 'Daily AMFI Sync Complete',
        message: evt.message || `Synchronized ${evt.count ? evt.count.toLocaleString() : 'all'} schemes at ${evt.timestamp}`,
        type: 'success',
        icon: '✅'
      });
    } else if (evt.status === 'in_progress') {
      showToast({
        title: 'AMFI Synchronizing...',
        message: evt.message || 'Fetching latest NAV text file from official AMFI servers...',
        type: 'info',
        icon: '⏳'
      });
    } else if (evt.status === 'failed') {
      showToast({
        title: 'AMFI Sync Alert',
        message: evt.message || 'Nightly sync encountered a connection issue.',
        type: 'error',
        icon: '⚠️'
      });
    }
  });

  // ──────────────────────────────────────────────────────────────────────────
  // 6. UI BADGE & TOAST CONTROLLERS
  // ──────────────────────────────────────────────────────────────────────────

  function updateBadgeStatus(isLive, labelText) {
    const badge = document.getElementById('wsStreamStatusBadge');
    const dot = document.getElementById('wsStreamDot');
    const text = document.getElementById('wsStreamText');

    if (!badge || !dot || !text) return;

    if (isLive) {
      badge.style.background = 'rgba(16, 185, 129, 0.12)';
      badge.style.borderColor = 'rgba(16, 185, 129, 0.35)';
      badge.style.color = '#34D399';
      dot.style.background = '#34D399';
      dot.style.boxShadow = '0 0 8px #34D399';
      text.textContent = labelText || 'WS LIVE';
    } else {
      badge.style.background = 'rgba(239, 68, 68, 0.12)';
      badge.style.borderColor = 'rgba(239, 68, 68, 0.35)';
      badge.style.color = '#F87171';
      dot.style.background = '#F87171';
      dot.style.boxShadow = '0 0 8px #F87171';
      text.textContent = labelText || 'OFFLINE';
    }
  }

  window.showToast = function ({ title, message, type = 'info', icon = '🔔', durationMs = 5000 }) {
    let container = document.getElementById('wsToastContainer');
    if (!container) {
      container = document.createElement('div');
      container.id = 'wsToastContainer';
      container.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        display: flex;
        flex-direction: column;
        gap: 10px;
        z-index: 999999;
        pointer-events: none;
      `;
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = 'ws-stream-toast';
    toast.style.cssText = `
      pointer-events: auto;
      background: rgba(13, 21, 36, 0.95);
      border: 1px solid ${type === 'success' ? 'rgba(52,211,153,0.4)' : (type === 'error' ? 'rgba(248,113,113,0.4)' : 'rgba(0,210,255,0.4)')};
      border-radius: 12px;
      padding: 12px 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.6), 0 0 15px ${type === 'success' ? 'rgba(52,211,153,0.15)' : 'rgba(0,210,255,0.15)'};
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      display: flex;
      align-items: flex-start;
      gap: 12px;
      min-width: 280px;
      max-width: 380px;
      transform: translateY(20px);
      opacity: 0;
      transition: all 250ms cubic-bezier(0.16, 1, 0.3, 1);
    `;

    toast.innerHTML = `
      <div style="font-size: 20px; line-height: 1; flex-shrink: 0; margin-top: 2px;">${icon}</div>
      <div style="flex: 1;">
        <div style="font-size: 12.5px; font-weight: 800; color: #F1F5F9; margin-bottom: 2px;">${title}</div>
        <div style="font-size: 11px; color: #94A3B8; line-height: 1.4;">${message}</div>
      </div>
      <button onclick="this.parentElement.remove()" style="background:none; border:none; color:#64748B; font-size:14px; cursor:pointer; padding:0 0 0 8px; line-height:1;">✕</button>
    `;

    container.appendChild(toast);

    // Animate In
    requestAnimationFrame(() => {
      toast.style.transform = 'translateY(0)';
      toast.style.opacity = '1';
    });

    // Auto dismiss
    setTimeout(() => {
      toast.style.transform = 'translateY(15px)';
      toast.style.opacity = '0';
      setTimeout(() => toast.remove(), 250);
    }, durationMs);
  };

  // ──────────────────────────────────────────────────────────────────────────
  // 7. INTERACTIVE WEBSOCKET DIAGNOSTICS MODAL
  // ──────────────────────────────────────────────────────────────────────────

  window.toggleWsStatsModal = function () {
    let modal = document.getElementById('wsDiagnosticsModal');
    if (!modal) {
      createDiagnosticsModal();
      modal = document.getElementById('wsDiagnosticsModal');
    }
    updateDiagnosticsUI();
    modal.style.display = modal.style.display === 'flex' ? 'none' : 'flex';
  };

  window.closeWsStatsModal = function () {
    const modal = document.getElementById('wsDiagnosticsModal');
    if (modal) modal.style.display = 'none';
  };

  function createDiagnosticsModal() {
    const div = document.createElement('div');
    div.id = 'wsDiagnosticsModal';
    div.onclick = function (e) {
      if (e.target === this) window.closeWsStatsModal();
    };
    div.style.cssText = `
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(6, 10, 16, 0.85);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      z-index: 999999;
      justify-content: center;
      align-items: center;
      padding: 16px;
    `;

    div.innerHTML = `
      <div style="background: #0D1626; border: 1px solid rgba(0,210,255,0.3); border-radius: 16px; width: 440px; max-width: 95vw; box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 30px rgba(0,210,255,0.15); overflow: hidden; animation: popIn 200ms ease;">
        <div style="padding: 16px 20px; border-bottom: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: space-between; align-items: center; background: rgba(255,255,255,0.02);">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 16px;">🌐</span>
            <span style="font-size: 13px; font-weight: 800; color: #F1F5F9; letter-spacing: -0.2px;">WebSocket Live Streaming Diagnostics</span>
          </div>
          <button onclick="window.closeWsStatsModal()" style="background: none; border: none; color: #64748B; font-size: 16px; cursor: pointer;">✕</button>
        </div>
        <div style="padding: 18px 20px; display: flex; flex-direction: column; gap: 12px; font-size: 11.5px;">
          <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8;">Connection Status:</span>
            <span id="wsDiagStatus" style="font-weight: 800; color: #34D399;">🟢 ACTIVE</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8;">Transport Protocol:</span>
            <span id="wsDiagTransport" style="font-weight: 700; color: #38BDF8; font-family: monospace;">websocket</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8;">Client Latency (RTT):</span>
            <span id="wsDiagLatency" style="font-weight: 800; color: #34D399; font-family: monospace;">-- ms</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8;">Socket SID:</span>
            <span id="wsDiagSid" style="color: #CBD5E1; font-family: monospace; font-size: 10px;">--</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8;">Packets Streamed:</span>
            <span id="wsDiagPackets" style="font-weight: 700; color: #F1F5F9;">0</span>
          </div>
          <div style="display: flex; justify-content: space-between; padding-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05);">
            <span style="color: #94A3B8;">Connected Browser Tabs:</span>
            <span id="wsDiagPeers" style="font-weight: 700; color: #A78BFA;">1</span>
          </div>
          <div style="display: flex; justify-content: space-between;">
            <span style="color: #94A3B8;">Last Broadcast Tick:</span>
            <span id="wsDiagLastTick" style="color: #CBD5E1;">Just now</span>
          </div>
          <div style="display: flex; gap: 8px; margin-top: 6px;">
            <button onclick="window.sendManualWsPing()" style="flex: 1; padding: 7px; border-radius: 8px; background: rgba(56,189,248,0.15); border: 1px solid rgba(56,189,248,0.3); color: #38BDF8; font-size: 11px; font-weight: 800; cursor: pointer;">
              ⚡ Send Test Ping
            </button>
            <button onclick="window.reconnectWebSocket()" style="flex: 1; padding: 7px; border-radius: 8px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #CBD5E1; font-size: 11px; font-weight: 700; cursor: pointer;">
              🔄 Reconnect
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(div);
  }

  function updateDiagnosticsUI() {
    const statusEl = document.getElementById('wsDiagStatus');
    const transEl = document.getElementById('wsDiagTransport');
    const latEl = document.getElementById('wsDiagLatency');
    const sidEl = document.getElementById('wsDiagSid');
    const pktsEl = document.getElementById('wsDiagPackets');
    const peersEl = document.getElementById('wsDiagPeers');
    const lastEl = document.getElementById('wsDiagLastTick');

    if (!statusEl) return;

    statusEl.innerHTML = window.MF_WS_STATE.connected ? '🟢 ACTIVE STREAM' : '🔴 DISCONNECTED';
    statusEl.style.color = window.MF_WS_STATE.connected ? '#34D399' : '#F87171';
    if (transEl) transEl.textContent = window.MF_WS_STATE.activeTransport;
    if (latEl) latEl.textContent = `${window.MF_WS_STATE.latencyMs} ms`;
    if (sidEl) sidEl.textContent = window.MF_WS_STATE.socketId || 'N/A';
    if (pktsEl) pktsEl.textContent = window.MF_WS_STATE.packetsReceived.toLocaleString();
    if (peersEl) peersEl.textContent = window.MF_WS_STATE.connectedClients;
    if (lastEl && window.MF_WS_STATE.lastTickTime) lastEl.textContent = window.MF_WS_STATE.lastTickTime;
  }

  window.sendManualWsPing = function () {
    sendPing();
    showToast({ title: 'Ping Sent', message: 'Calculated latency round-trip time with backend server.', type: 'info', icon: '⚡', durationMs: 2500 });
  };

  window.reconnectWebSocket = function () {
    if (socket) {
      socket.disconnect().connect();
      showToast({ title: 'Reconnecting', message: 'Re-initiating WebSocket handshake...', type: 'info', icon: '🔄', durationMs: 2000 });
    }
  };

})();
