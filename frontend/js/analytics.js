(function () {
  const canvas = document.getElementById("analyticsChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");

  const chartData = {
    reach: [500, 620, 660, 740, 760, 820, 910, 970, 1080, 1040, 1200, 1160, 1260, 1420, 1380],
    likes: [180, 220, 210, 295, 310, 370, 390, 430, 450, 430, 490, 520, 555, 610, 585]
  };

  function drawChart() {
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const dpr = window.devicePixelRatio || 1;

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const pad = 22;
    const chartW = width - pad * 2;
    const chartH = height - pad * 2;

    ctx.clearRect(0, 0, width, height);

    ctx.strokeStyle = "rgba(255,255,255,0.08)";
    ctx.lineWidth = 1;
    for (let i = 0; i <= 4; i++) {
      const y = pad + (chartH / 4) * i;
      ctx.beginPath();
      ctx.moveTo(pad, y);
      ctx.lineTo(width - pad, y);
      ctx.stroke();
    }

    const maxValue = Math.max(...chartData.reach.concat(chartData.likes), 1);

    function plotSeries(values, color) {
      ctx.beginPath();
      values.forEach((value, index) => {
        const x = pad + (index / (values.length - 1)) * chartW;
        const y = height - pad - (value / maxValue) * chartH;
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = color;
      ctx.lineWidth = 2.5;
      ctx.stroke();
    }

    plotSeries(chartData.reach, "#45baf0");
    plotSeries(chartData.likes, "#9efb5d");
  }

  const observer = new ResizeObserver(drawChart);
  observer.observe(canvas);
  drawChart();
})();
