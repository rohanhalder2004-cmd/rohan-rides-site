(function () {
  const backendBase = "http://127.0.0.1:5000";

  const appState = {
    profile: {},
    reels: [],
    analytics: [],
    backendReady: false
  };

  function setText(selector, value) {
    const el = document.querySelector(selector);
    if (el) el.textContent = value;
  }

  function formatCompact(value) {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return String(value);
  }

  async function fetchJson(url) {
    const response = await fetch(url, { headers: { accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`);
    }
    return response.json();
  }

  async function loadBackendData() {
    try {
      const profileRes = await fetchJson(`${backendBase}/api/profile`);
      const reelsRes = await fetchJson(`${backendBase}/api/reels`);
      const analyticsRes = await fetchJson(`${backendBase}/api/analytics`);

      appState.profile = profileRes.profile || {};
      appState.reels = Array.isArray(reelsRes.items) ? reelsRes.items : [];
      appState.analytics = Array.isArray(analyticsRes.days) ? analyticsRes.days : [];
      appState.backendReady = true;
      console.log("Backend connected:", appState);
    } catch (error) {
      console.warn("Backend not available, using demo mode.", error.message);
      appState.backendReady = false;
    }
  }

  function applyProfileValues() {
    const profile = appState.profile;
    const followers = Number(profile.followers || 12800);
    const likes = Number(profile.total_likes || 86400);
    const totalReels = Number(profile.total_reels || 42);
    const totalViews = Number(profile.total_views || 1200000);

    setText("#followersValue", formatCompact(followers));
    setText("#likesValue", formatCompact(likes));
    setText("#reelsValue", String(totalReels));
    setText("#viewsValue", formatCompact(totalViews));
  }

  document.getElementById("year").textContent = new Date().getFullYear();
  document.getElementById("rideOnBtn").addEventListener("click", () => {
    document.getElementById("reels")?.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  loadBackendData().finally(() => {
    if (appState.backendReady && Object.keys(appState.profile).length > 0) {
      applyProfileValues();
    }
  });
})();
