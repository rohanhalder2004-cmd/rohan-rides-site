(function () {
  const reelState = {
    index: 0,
    reels: [],
    autoplayTimer: null
  };

  const ui = {
    title: document.getElementById("reelTitle"),
    caption: document.getElementById("reelCaption"),
    song: document.getElementById("reelSong"),
    views: document.getElementById("reelViews"),
    likes: document.getElementById("reelLikes"),
    date: document.getElementById("reelDate"),
    description: document.getElementById("reelDescription"),
    visualTitle: document.getElementById("reelVisualTitle"),
    counter: document.getElementById("reelCounter"),
    ambilight: document.getElementById("ambilight"),
    reelCard: document.querySelector(".reel-card"),
    visual: document.getElementById("reelVisual"),
    prev: document.getElementById("prevReel"),
    next: document.getElementById("nextReel"),
    soundToggle: document.getElementById("soundToggle")
  };

  function formatNumber(value) {
    if (!value) return "0";
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
    return String(value);
  }

  function getDemoReels() {
    return [
      {
        title: "Midnight Miles",
        caption: "Some roads feel like they understand you. 🖤",
        song: "Demo track · Night Drive",
        views: 128000,
        likes: 9400,
        date: "NOV 08",
        description: "A late-night ride, a little music, and the kind of calm you only find on an open road.",
        glow: "#2cc0a7",
        gradientA: "#112d2f",
        gradientB: "#214d5b"
      },
      {
        title: "Blue Hour Ride",
        caption: "Chasing the last light of the day 💙",
        song: "Demo track · Blue Hour",
        views: 96000,
        likes: 7100,
        date: "OCT 27",
        description: "That blue-hour sky makes every ride feel like a scene from a movie.",
        glow: "#2395ff",
        gradientA: "#122548",
        gradientB: "#1e4f80"
      },
      {
        title: "Ride With Heart",
        caption: "Two wheels, one heart, endless roads 💚",
        song: "Demo track · Ride With Me",
        views: 214000,
        likes: 18000,
        date: "OCT 12",
        description: "A little love in the caption, a song in the helmet, and nowhere else to be.",
        glow: "#ff9d45",
        gradientA: "#3b291d",
        gradientB: "#86613d"
      }
    ];
  }

  function renderReel() {
    const reel = reelState.reels[reelState.index];
    if (!reel) return;

    ui.title.textContent = reel.title;
    ui.caption.textContent = reel.caption;
    ui.song.textContent = `♫ ${reel.song}`;
    ui.views.textContent = formatNumber(reel.views);
    ui.likes.textContent = formatNumber(reel.likes);
    ui.date.textContent = reel.date;
    ui.description.textContent = reel.description;
    ui.visualTitle.textContent = reel.title;
    ui.counter.textContent = `${String(reelState.index + 1).padStart(2, "0")} / ${String(reelState.reels.length).padStart(2, "0")}`;

    ui.visual.style.background = `linear-gradient(180deg, rgba(4,8,12,0.12), rgba(6,11,14,0.72)), linear-gradient(120deg, ${reel.gradientA}, ${reel.gradientB})`;
    ui.ambilight.style.background = `radial-gradient(circle at 50% 50%, ${reel.glow}, transparent 58%)`;
  }

  function nextReel() {
    reelState.index = (reelState.index + 1) % reelState.reels.length;
    renderReel();
    restartAutoplay();
  }

  function prevReel() {
    reelState.index = (reelState.index - 1 + reelState.reels.length) % reelState.reels.length;
    renderReel();
    restartAutoplay();
  }

  function restartAutoplay() {
    clearInterval(reelState.autoplayTimer);
    reelState.autoplayTimer = setInterval(() => {
      nextReel();
    }, 5000);
  }

  let swipeStartX = 0;
  if (ui.reelCard) {
    ui.reelCard.addEventListener("touchstart", (event) => {
      swipeStartX = event.changedTouches[0].screenX;
    }, { passive: true });

    ui.reelCard.addEventListener("touchend", (event) => {
      const diff = event.changedTouches[0].screenX - swipeStartX;
      if (Math.abs(diff) > 50) {
        if (diff < 0) nextReel();
        else prevReel();
      }
    }, { passive: true });
  }

  if (ui.prev) ui.prev.addEventListener("click", prevReel);
  if (ui.next) ui.next.addEventListener("click", nextReel);

  if (ui.soundToggle) {
    ui.soundToggle.addEventListener("click", () => {
      const currentlyMuted = ui.soundToggle.getAttribute("data-muted") === "true";
      ui.soundToggle.setAttribute("data-muted", String(!currentlyMuted));
      ui.soundToggle.textContent = currentlyMuted ? "Sound is off · demo preview" : "Sound is on · demo preview";
      ui.soundToggle.setAttribute("aria-pressed", String(!currentlyMuted));
    });
  }

  reelState.reels = getDemoReels();
  renderReel();
  restartAutoplay();
})();
