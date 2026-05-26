import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const dataDir = path.join(root, "data");
const d3Dir = path.join(root, "d3");

fs.mkdirSync(dataDir, { recursive: true });
fs.mkdirSync(d3Dir, { recursive: true });

const nberRecessions = [
  ["1929-08-01", "1933-03-01", "Great Depression"],
  ["1937-05-01", "1938-06-01", "1937-1938 recession"],
  ["1945-02-01", "1945-10-01", "Postwar recession"],
  ["1948-11-01", "1949-10-01", "1948-1949 recession"],
  ["1953-07-01", "1954-05-01", "1953-1954 recession"],
  ["1957-08-01", "1958-04-01", "1957-1958 recession"],
  ["1960-04-01", "1961-02-01", "1960-1961 recession"],
  ["1969-12-01", "1970-11-01", "1969-1970 recession"],
  ["1973-11-01", "1975-03-01", "1973-1975 recession"],
  ["1980-01-01", "1980-07-01", "1980 recession"],
  ["1981-07-01", "1982-11-01", "1981-1982 recession"],
  ["1990-07-01", "1991-03-01", "1990-1991 recession"],
  ["2001-03-01", "2001-11-01", "2001 recession"],
  ["2007-12-01", "2009-06-01", "Global Financial Crisis"],
  ["2020-02-01", "2020-04-01", "COVID recession"]
].map(([start, end, label]) => ({ start, end, label }));

function writeJson(fileName, value) {
  const outPath = path.join(dataDir, fileName);
  fs.writeFileSync(outPath, `${JSON.stringify(value, null, 2)}\n`);
  return outPath;
}

function writeHtml(fileName, title, desc, dataFile, fallbackData, drawScript) {
  const outPath = path.join(d3Dir, fileName);
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${title}</title>
  <style>
    :root {
      --color-white: #FFFFFF;
      --color-ink: #000000;
      --color-red: #C8102E;
      --color-gold: #A4804A;
      --color-secondary: #555555;
      --color-border: #CCCCCC;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --color-white: #111111;
        --color-ink: #F0F0F0;
        --color-red: #E8243A;
        --color-gold: #C49A5A;
        --color-secondary: #999999;
        --color-border: #333333;
      }
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--color-white);
      color: var(--color-ink);
      font-family: 'Real Head Pro', 'FF Real', Lato, sans-serif;
    }
    #chart {
      width: 100vw;
      min-height: 640px;
      padding: 24px;
    }
    .chart-title {
      font-family: 'Real Head Pro', 'FF Real', Lato, sans-serif;
      font-size: 16px;
      font-weight: 700;
      fill: var(--color-ink);
    }
    .chart-subtitle, .axis-label, .tick text, .annotation-label, .source-line,
    .legend-label, .small-label {
      font-family: 'Real Head Pro', 'FF Real', Lato, sans-serif;
      fill: var(--color-secondary);
    }
    .tick line, .axis-domain, .gridline {
      stroke: var(--color-border);
    }
    .tooltip {
      position: absolute;
      pointer-events: none;
      opacity: 0;
      max-width: 260px;
      padding: 8px 10px;
      border: 1px solid var(--color-border);
      border-left: 3px solid var(--color-gold);
      background: var(--color-white);
      color: var(--color-ink);
      font: 13px/1.35 'Real Head Pro', 'FF Real', Lato, sans-serif;
      box-shadow: 0 1px 2px rgb(0 0 0 / 0.06);
    }
    @media (prefers-reduced-motion: reduce) {
      * { transition: none !important; animation: none !important; }
    }
  </style>
</head>
<body>
  <div id="chart" role="main"></div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.9.0/d3.min.js"></script>
  <script>
    const FALLBACK_DATA = ${JSON.stringify(fallbackData)};
    async function loadData() {
      try {
        return await d3.json('../data/${dataFile}');
      } catch {
        return FALLBACK_DATA;
      }
    }
    const tooltip = d3.select('body').append('div').attr('class', 'tooltip');
    function showTooltip(event, html) {
      tooltip.html(html)
        .style('left', (event.pageX + 12) + 'px')
        .style('top', (event.pageY - 28) + 'px')
        .transition().duration(150).style('opacity', 1);
    }
    function moveTooltip(event) {
      tooltip
        .style('left', (event.pageX + 12) + 'px')
        .style('top', (event.pageY - 28) + 'px');
    }
    function hideTooltip() {
      tooltip.transition().duration(100).style('opacity', 0);
    }
    ${drawScript}
  </script>
</body>
</html>
`;
  fs.writeFileSync(outPath, html);
  return outPath;
}

function seededRandom(seed = 7) {
  let t = seed >>> 0;
  return () => {
    t += 0x6D2B79F5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function recessionFlag(dateString) {
  const t = Date.parse(dateString);
  return nberRecessions.some(d => t >= Date.parse(d.start) && t <= Date.parse(d.end));
}

function monthsBetween(startYear, endYear) {
  const rows = [];
  for (let y = startYear; y <= endYear; y += 1) {
    for (let m = 0; m < 12; m += 1) {
      rows.push(`${y}-${String(m + 1).padStart(2, "0")}-01`);
    }
  }
  return rows;
}

function makeTdaSignals() {
  const rand = seededRandom(11);
  const rows = monthsBetween(1927, 2026).map((date, i) => {
    const year = Number(date.slice(0, 4));
    const rec = recessionFlag(date);
    const cycle = Math.sin(i / 23) * 0.35 + Math.sin(i / 71) * 0.45;
    const crisis = rec ? 0.8 + rand() * 0.7 : 0;
    const covid = year === 2020 ? 1.8 : 0;
    const gfc = year >= 2008 && year <= 2009 ? 1.1 : 0;
    const h0 = cycle + crisis + covid + (rand() - 0.5) * 0.9;
    const h1Inv = -0.12 + crisis * 1.1 + gfc + covid * 0.7 + Math.sin(i / 17) * 0.22 + (rand() - 0.5) * 0.7;
    const composite = h0 * 0.22 + h1Inv * 0.48 + Math.sin(i / 37) * 0.22 + (rand() - 0.5) * 0.45;
    return {
      date,
      recession: rec,
      h0LandscapeZ: Number(h0.toFixed(3)),
      inverseH1LandscapeZ: Number(h1Inv.toFixed(3)),
      compositeZ: Number(composite.toFixed(3))
    };
  });
  return { notes: "Generated companion series shaped to match manuscript signal descriptions; replace with model output when available.", recessions: nberRecessions, rows };
}

function makeLeadCorrelation() {
  const rows = [];
  for (let lag = -100; lag <= 250; lag += 5) {
    const peak = 0.105 * Math.exp(-Math.pow((lag - 31) / 42, 2));
    const longTail = 0.035 * Math.exp(-Math.pow((lag - 185) / 30, 2));
    const pre = 0.03 * Math.exp(-Math.pow((lag + 20) / 26, 2));
    const wave = Math.sin(lag / 13) * 0.008;
    rows.push({ lag, correlation: Number((peak + longTail + pre + wave - 0.005).toFixed(4)) });
  }
  return {
    notes: "Generated cross-correlation profile matching manuscript: small positive lead association around 31 trading days and stronger contemporaneous/post-onset association.",
    rows,
    peakLag: 31,
    peakCorrelation: 0.10
  };
}

function makeEventStudy() {
  const rand = seededRandom(21);
  const mean = [];
  for (let day = -250; day <= 126; day += 2) {
    const preRise = 0.22 * Math.exp(-Math.pow((day + 35) / 45, 2));
    const onset = 0.36 * Math.exp(-Math.pow((day - 18) / 55, 2));
    const baseline = 0.05 * Math.sin(day / 19);
    const value = preRise + onset + baseline + (rand() - 0.5) * 0.05;
    const se = 0.18 + 0.08 * Math.exp(-Math.pow(day / 80, 2));
    mean.push({ day, mean: Number(value.toFixed(3)), lower: Number((value - 1.96 * se).toFixed(3)), upper: Number((value + 1.96 * se).toFixed(3)) });
  }
  return {
    notes: "Generated event-study companion data aligned to recession onset; replace with event-window output when available.",
    rows: mean,
    onsetDay: 0
  };
}

function makeEpisodeHeatmap() {
  const rand = seededRandom(31);
  const episodes = [
    "1937-1938", "1945-1945", "1948-1949", "1953-1954", "1957-1958",
    "1960-1961", "1969-1970", "1973-1975", "1980-1980", "1981-1982",
    "1990-1991", "2001-2001", "2007-2009", "2020-2020"
  ];
  const cells = [];
  episodes.forEach((episode, r) => {
    for (let day = -250; day <= 126; day += 5) {
      const episodeBoost = r >= 11 ? 0.35 : r >= 7 ? 0.22 : 0.08;
      const onset = episodeBoost * Math.exp(-Math.pow((day - 10) / 60, 2));
      const pre = 0.16 * Math.exp(-Math.pow((day + 55) / 70, 2));
      const value = onset + pre + Math.sin((day + r * 8) / 24) * 0.22 + (rand() - 0.5) * 1.15;
      cells.push({ episode, day, value: Number(Math.max(-3, Math.min(3, value)).toFixed(3)) });
    }
  });
  return {
    notes: "Generated episode heatmap companion data for visual reconstruction; rows represent recession episodes and day offsets relative to onset.",
    episodes,
    cells
  };
}

function makeRocCurves() {
  const models = [
    { id: "vol", label: "Volatility only", auc: 0.7725, role: "neutral" },
    { id: "corr", label: "Avg correlation only", auc: 0.7040, role: "neutral" },
    { id: "baseline", label: "Volatility + returns", auc: 0.7827, role: "red" },
    { id: "tda", label: "TDA only", auc: 0.6707, role: "ink" },
    { id: "tdaBaseline", label: "TDA + baseline", auc: 0.7383, role: "secondary" },
    { id: "random", label: "Random", auc: 0.5, role: "random" }
  ];
  const curves = models.map(model => {
    const a = model.auc === 0.5 ? 1 : model.auc / (1 - model.auc);
    const points = [];
    for (let i = 0; i <= 80; i += 1) {
      const fpr = i / 80;
      const tpr = model.id === "random" ? fpr : 1 - Math.pow(1 - fpr, a);
      points.push({ fpr: Number(fpr.toFixed(4)), tpr: Number(Math.max(0, Math.min(1, tpr)).toFixed(4)) });
    }
    return { ...model, points };
  });
  return { notes: "Generated smooth ROC curves from manuscript AUC targets. Curve shapes are illustrative; AUC values match the table targets.", curves };
}

const figure1Data = JSON.parse(fs.readFileSync(path.join(dataDir, "figure-1-yearly-correlation.json"), "utf8"));
const figure2Data = makeTdaSignals();
const figure3Data = makeLeadCorrelation();
const figure4Data = makeEventStudy();
const figure5Data = makeEpisodeHeatmap();
const figure6Data = makeRocCurves();

writeJson("figure-2-tda-crisis-signals.json", figure2Data);
writeJson("figure-3-lead-cross-correlation.json", figure3Data);
writeJson("figure-4-recession-event-study.json", figure4Data);
writeJson("figure-5-recession-episode-heatmap.json", figure5Data);
writeJson("figure-6-roc-curves.json", figure6Data);

const commonHeader = `
function addHeader(svg, margin, title, subtitle) {
  svg.append('text').attr('class', 'chart-title').attr('x', margin.left).attr('y', 24).text(title);
  svg.append('text').attr('class', 'chart-subtitle').attr('x', margin.left).attr('y', 44).attr('font-size', 13).text(subtitle);
}
function addSource(svg, margin, totalHeight, source) {
  svg.append('text').attr('class', 'source-line').attr('x', margin.left).attr('y', totalHeight - 4).attr('font-size', 11).text(source);
}
function finishAxes(g) {
  g.selectAll('.domain').attr('class', 'axis-domain').attr('stroke', 'var(--color-ink)');
  g.selectAll('.tick text').attr('font-size', 11);
}
`;

writeHtml(
  "figure-1-mean-absolute-correlation.html",
  "Figure 1: Mean absolute cross-industry correlation",
  "Yearly mean absolute pairwise return correlation across Fama-French 49 industry portfolios.",
  "figure-1-yearly-correlation.json",
  figure1Data,
  `${commonHeader}
const recessions = [
  { label: 'Great Depression', year: 1929 },
  { label: 'Oil embargo', year: 1973 },
  { label: 'Dot-com', year: 2001 },
  { label: 'GFC', year: 2008 },
  { label: 'COVID', year: 2020 }
];
function draw(data) {
  d3.select('#chart').selectAll('*').remove();
  const container = document.getElementById('chart');
  const totalWidth = container.clientWidth || 1000;
  const totalHeight = Math.max(560, Math.round(totalWidth * 0.46));
  const margin = { top: 72, right: 40, bottom: 72, left: 72 };
  const chartWidth = totalWidth - margin.left - margin.right;
  const chartHeight = totalHeight - margin.top - margin.bottom;
  const svg = d3.select('#chart').append('svg').attr('width', totalWidth).attr('height', totalHeight).attr('role', 'img').attr('aria-labelledby', 'fig-title fig-desc');
  svg.append('title').attr('id', 'fig-title').text('Mean absolute cross-industry correlation by year');
  svg.append('desc').attr('id', 'fig-desc').text('Yearly mean absolute pairwise return correlation across Fama-French 49 industry portfolios.');
  addHeader(svg, margin, 'Mean absolute cross-industry correlation by year', 'Fama-French 49 daily industry portfolios, value-weighted returns');
  const gChart = svg.append('g').attr('class', 'g-chart').attr('transform', \`translate(\${margin.left},\${margin.top})\`);
  const xScaleUtc = d3.scaleUtc().domain(d3.extent(data, d => new Date(Date.UTC(d.year, 0, 1)))).range([0, chartWidth]);
  const yScaleLinear = d3.scaleLinear().domain([0, Math.max(0.85, d3.max(data, d => d.meanAbsCorrelation) * 1.08)]).nice().range([chartHeight, 0]);
  const area = d3.area().x(d => xScaleUtc(new Date(Date.UTC(d.year, 0, 1)))).y0(chartHeight).y1(d => yScaleLinear(d.meanAbsCorrelation));
  const line = d3.line().x(d => xScaleUtc(new Date(Date.UTC(d.year, 0, 1)))).y(d => yScaleLinear(d.meanAbsCorrelation));
  gChart.append('g').attr('class', 'g-gridlines').call(d3.axisLeft(yScaleLinear).ticks(6).tickSize(-chartWidth).tickFormat('')).selectAll('line').attr('class', 'gridline').attr('stroke-opacity', 0.6);
  gChart.select('.g-gridlines .domain').remove();
  gChart.append('path').datum(data).attr('fill', 'var(--color-red)').attr('fill-opacity', 0.13).attr('d', area);
  gChart.append('path').datum(data).attr('fill', 'none').attr('stroke', 'var(--color-red)').attr('stroke-width', 2.25).attr('d', line);
  gChart.selectAll('.data-point').data(data).join('circle').attr('class', 'data-point').attr('cx', d => xScaleUtc(new Date(Date.UTC(d.year, 0, 1)))).attr('cy', d => yScaleLinear(d.meanAbsCorrelation)).attr('r', 3).attr('fill', 'var(--color-white)').attr('stroke', 'var(--color-red)').attr('stroke-width', 1.5).attr('opacity', 0).attr('tabindex', 0).attr('aria-label', d => \`\${d.year}: mean absolute correlation \${d.meanAbsCorrelation.toFixed(3)}\`).on('mouseover focus', function(event, d) { d3.select(this).attr('opacity', 1).attr('r', 4.5); showTooltip(event, \`<strong>\${d.year}</strong><br>Mean |rho|: \${d.meanAbsCorrelation.toFixed(3)}<br>Pairs used: \${d.pairsUsed}\`); }).on('mousemove', moveTooltip).on('mouseout blur', function() { d3.select(this).attr('opacity', 0).attr('r', 3); hideTooltip(); });
  const gAnnotations = gChart.append('g').attr('class', 'g-annotations');
  gAnnotations.selectAll('.event-line').data(recessions).join('line').attr('x1', d => xScaleUtc(new Date(Date.UTC(d.year, 0, 1)))).attr('x2', d => xScaleUtc(new Date(Date.UTC(d.year, 0, 1)))).attr('y1', 0).attr('y2', chartHeight).attr('stroke', 'var(--color-ink)').attr('stroke-width', 1).attr('stroke-dasharray', '4 4').attr('stroke-opacity', 0.28);
  gAnnotations.selectAll('.annotation-label').data(recessions).join('text').attr('class', 'annotation-label').attr('x', d => xScaleUtc(new Date(Date.UTC(d.year, 0, 1))) + 4).attr('y', 16).attr('font-size', 11).text(d => d.label);
  gChart.append('g').attr('transform', \`translate(0,\${chartHeight})\`).call(d3.axisBottom(xScaleUtc).ticks(d3.utcYear.every(10)).tickFormat(d3.utcFormat('%Y')));
  gChart.append('g').call(d3.axisLeft(yScaleLinear).ticks(6).tickFormat(d3.format('.1f')));
  finishAxes(gChart);
  svg.append('text').attr('class', 'axis-label').attr('x', margin.left + chartWidth / 2).attr('y', totalHeight - 24).attr('text-anchor', 'middle').attr('font-size', 12).text('Year');
  svg.append('text').attr('class', 'axis-label').attr('transform', \`translate(20,\${margin.top + chartHeight / 2}) rotate(-90)\`).attr('text-anchor', 'middle').attr('font-size', 12).text('Mean absolute correlation');
  addSource(svg, margin, totalHeight, 'Source: Kenneth R. French Data Library, 49 Industry Portfolios Daily, downloaded 2026-05-26.');
}
loadData().then(data => { draw(data); new ResizeObserver(() => draw(data)).observe(document.getElementById('chart')); });`
);

writeHtml(
  "figure-2-tda-crisis-signals.html",
  "Figure 2: TDA crisis signals across recession regimes",
  "Three topological signal series with NBER recession bands.",
  "figure-2-tda-crisis-signals.json",
  figure2Data,
  `${commonHeader}
function draw(payload) {
  d3.select('#chart').selectAll('*').remove();
  const data = payload.rows;
  const container = document.getElementById('chart');
  const totalWidth = container.clientWidth || 1100;
  const totalHeight = Math.max(720, Math.round(totalWidth * 0.62));
  const margin = { top: 76, right: 40, bottom: 64, left: 72 };
  const chartWidth = totalWidth - margin.left - margin.right;
  const rowGap = 34;
  const rowHeight = (totalHeight - margin.top - margin.bottom - rowGap * 2) / 3;
  const svg = d3.select('#chart').append('svg').attr('width', totalWidth).attr('height', totalHeight).attr('role', 'img').attr('aria-labelledby', 'fig-title fig-desc');
  svg.append('title').attr('id', 'fig-title').text('TDA crisis signals across recession regimes');
  svg.append('desc').attr('id', 'fig-desc').text('Three time-series panels show generated topological signal companions with NBER recession windows shaded.');
  addHeader(svg, margin, 'TDA crisis signals across recession regimes', 'Generated companion data; replace JSON with rolling persistent-homology output when available');
  const x = d3.scaleUtc().domain(d3.extent(data, d => new Date(d.date))).range([0, chartWidth]);
  const panels = [
    { key: 'h0LandscapeZ', label: 'H0 landscape norm Z', color: 'var(--color-ink)' },
    { key: 'inverseH1LandscapeZ', label: '-H1 landscape norm Z', color: '#787878' },
    { key: 'compositeZ', label: 'Composite TDA signal Z', color: 'var(--color-red)' }
  ];
  panels.forEach((panel, i) => {
    const top = margin.top + i * (rowHeight + rowGap);
    const g = svg.append('g').attr('transform', \`translate(\${margin.left},\${top})\`);
    const extent = d3.extent(data, d => d[panel.key]);
    const y = d3.scaleLinear().domain([Math.min(-3, extent[0] * 1.12), Math.max(3, extent[1] * 1.12)]).nice().range([rowHeight, 0]);
    payload.recessions.forEach(r => {
      const x0 = x(new Date(r.start));
      const x1 = x(new Date(r.end));
      if (x1 >= 0 && x0 <= chartWidth) g.append('rect').attr('x', Math.max(0, x0)).attr('y', 0).attr('width', Math.max(1, Math.min(chartWidth, x1) - Math.max(0, x0))).attr('height', rowHeight).attr('fill', 'var(--color-border)').attr('opacity', 0.38);
    });
    g.append('g').call(d3.axisLeft(y).ticks(4).tickSize(-chartWidth).tickFormat('')).selectAll('line').attr('class', 'gridline').attr('stroke-opacity', 0.5);
    g.select('.domain').remove();
    g.append('line').attr('x1', 0).attr('x2', chartWidth).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', 'var(--color-border)');
    g.append('path').datum(data).attr('fill', 'none').attr('stroke', panel.color).attr('stroke-width', 1.45).attr('d', d3.line().x(d => x(new Date(d.date))).y(d => y(d[panel.key])));
    g.append('g').attr('transform', \`translate(0,\${rowHeight})\`).call(d3.axisBottom(x).ticks(i === 2 ? d3.utcYear.every(10) : d3.utcYear.every(20)).tickFormat(d3.utcFormat('%Y')));
    g.append('g').call(d3.axisLeft(y).ticks(4));
    finishAxes(g);
    g.append('text').attr('class', 'chart-title').attr('x', 0).attr('y', -12).attr('font-size', 13).text(panel.label);
    svg.append('text').attr('class', 'axis-label').attr('transform', \`translate(20,\${top + rowHeight / 2}) rotate(-90)\`).attr('text-anchor', 'middle').attr('font-size', 12).text('Z-score');
  });
  svg.append('text').attr('class', 'axis-label').attr('x', margin.left + chartWidth / 2).attr('y', totalHeight - 24).attr('text-anchor', 'middle').attr('font-size', 12).text('Date');
  addSource(svg, margin, totalHeight, 'Data: generated companion signals shaped to manuscript descriptions; NBER recession bands included.');
}
loadData().then(data => { draw(data); new ResizeObserver(() => draw(data)).observe(document.getElementById('chart')); });`
);

writeHtml(
  "figure-3-lead-cross-correlation.html",
  "Figure 3: Composite TDA signal lead cross-correlation",
  "Cross-correlation between composite topology and recession indicator by lag.",
  "figure-3-lead-cross-correlation.json",
  figure3Data,
  `${commonHeader}
function draw(payload) {
  d3.select('#chart').selectAll('*').remove();
  const data = payload.rows;
  const container = document.getElementById('chart');
  const totalWidth = container.clientWidth || 980;
  const totalHeight = Math.max(560, Math.round(totalWidth * 0.52));
  const margin = { top: 76, right: 40, bottom: 76, left: 72 };
  const chartWidth = totalWidth - margin.left - margin.right;
  const chartHeight = totalHeight - margin.top - margin.bottom;
  const svg = d3.select('#chart').append('svg').attr('width', totalWidth).attr('height', totalHeight).attr('role', 'img').attr('aria-labelledby', 'fig-title fig-desc');
  svg.append('title').attr('id', 'fig-title').text('Composite TDA signal lead cross-correlation');
  svg.append('desc').attr('id', 'fig-desc').text('Bars show correlation by trading-day lag, with positive lag meaning the TDA signal leads recession onset.');
  addHeader(svg, margin, 'Composite TDA signal lead cross-correlation', 'Positive lag means TDA leads the recession indicator; generated companion data');
  const g = svg.append('g').attr('transform', \`translate(\${margin.left},\${margin.top})\`);
  const x = d3.scaleBand().domain(data.map(d => d.lag)).range([0, chartWidth]).padding(0.1);
  const y = d3.scaleLinear().domain([Math.min(-0.03, d3.min(data, d => d.correlation) * 1.2), d3.max(data, d => d.correlation) * 1.18]).nice().range([chartHeight, 0]);
  g.append('g').call(d3.axisLeft(y).ticks(6).tickSize(-chartWidth).tickFormat('')).selectAll('line').attr('class', 'gridline').attr('stroke-opacity', 0.6);
  g.select('.domain').remove();
  g.append('line').attr('x1', 0).attr('x2', chartWidth).attr('y1', y(0)).attr('y2', y(0)).attr('stroke', 'var(--color-ink)').attr('stroke-width', 1);
  g.selectAll('.bar').data(data).join('rect').attr('class', 'bar').attr('x', d => x(d.lag)).attr('y', d => y(Math.max(0, d.correlation))).attr('width', x.bandwidth()).attr('height', d => Math.abs(y(d.correlation) - y(0))).attr('fill', d => d.lag >= 0 ? 'var(--color-red)' : '#ADADAD').attr('opacity', d => d.lag === 30 ? 1 : 0.72).attr('tabindex', 0).attr('aria-label', d => \`Lag \${d.lag} trading days, correlation \${d.correlation}\`).on('mouseover focus', (event, d) => showTooltip(event, \`<strong>Lag \${d.lag}</strong><br>Correlation: \${d.correlation.toFixed(3)}\`)).on('mousemove', moveTooltip).on('mouseout blur', hideTooltip);
  const xLinear = d3.scaleLinear().domain(d3.extent(data, d => d.lag)).range([x(data[0].lag) + x.bandwidth() / 2, x(data[data.length - 1].lag) + x.bandwidth() / 2]);
  g.append('line').attr('x1', xLinear(0)).attr('x2', xLinear(0)).attr('y1', 0).attr('y2', chartHeight).attr('stroke', 'var(--color-ink)').attr('stroke-dasharray', '4 4').attr('stroke-opacity', 0.6);
  g.append('line').attr('x1', xLinear(payload.peakLag)).attr('x2', xLinear(payload.peakLag)).attr('y1', 0).attr('y2', chartHeight).attr('stroke', 'var(--color-gold)').attr('stroke-width', 2);
  g.append('g').attr('transform', \`translate(0,\${chartHeight})\`).call(d3.axisBottom(xLinear).ticks(8).tickFormat(d3.format('d')));
  g.append('g').call(d3.axisLeft(y).ticks(6));
  finishAxes(g);
  svg.append('text').attr('class', 'axis-label').attr('x', margin.left + chartWidth / 2).attr('y', totalHeight - 28).attr('text-anchor', 'middle').attr('font-size', 12).text('Lag in trading days (positive = TDA leads)');
  svg.append('text').attr('class', 'axis-label').attr('transform', \`translate(20,\${margin.top + chartHeight / 2}) rotate(-90)\`).attr('text-anchor', 'middle').attr('font-size', 12).text('Correlation');
  addSource(svg, margin, totalHeight, 'Data: generated companion cross-correlation profile from manuscript targets.');
}
loadData().then(data => { draw(data); new ResizeObserver(() => draw(data)).observe(document.getElementById('chart')); });`
);

writeHtml(
  "figure-4-recession-event-study.html",
  "Figure 4: Composite TDA signal around recession onset",
  "Event-study line aligned to NBER recession onset.",
  "figure-4-recession-event-study.json",
  figure4Data,
  `${commonHeader}
function draw(payload) {
  d3.select('#chart').selectAll('*').remove();
  const data = payload.rows;
  const container = document.getElementById('chart');
  const totalWidth = container.clientWidth || 980;
  const totalHeight = Math.max(560, Math.round(totalWidth * 0.52));
  const margin = { top: 76, right: 40, bottom: 76, left: 72 };
  const chartWidth = totalWidth - margin.left - margin.right;
  const chartHeight = totalHeight - margin.top - margin.bottom;
  const svg = d3.select('#chart').append('svg').attr('width', totalWidth).attr('height', totalHeight).attr('role', 'img').attr('aria-labelledby', 'fig-title fig-desc');
  svg.append('title').attr('id', 'fig-title').text('Composite TDA signal around recession onset');
  svg.append('desc').attr('id', 'fig-desc').text('Mean event-study path and confidence band around recession onset, where day zero marks NBER recession onset.');
  addHeader(svg, margin, 'Composite TDA signal around recession onset', 'Mean event-study path aligned to recession onset; generated companion data');
  const g = svg.append('g').attr('transform', \`translate(\${margin.left},\${margin.top})\`);
  const x = d3.scaleLinear().domain(d3.extent(data, d => d.day)).range([0, chartWidth]);
  const y = d3.scaleLinear().domain([d3.min(data, d => d.lower) * 1.1, d3.max(data, d => d.upper) * 1.1]).nice().range([chartHeight, 0]);
  g.append('rect').attr('x', x(-60)).attr('y', 0).attr('width', x(0) - x(-60)).attr('height', chartHeight).attr('fill', 'var(--color-red)').attr('opacity', 0.08);
  g.append('g').call(d3.axisLeft(y).ticks(6).tickSize(-chartWidth).tickFormat('')).selectAll('line').attr('class', 'gridline').attr('stroke-opacity', 0.6);
  g.select('.domain').remove();
  g.append('path').datum(data).attr('fill', 'var(--color-red)').attr('fill-opacity', 0.15).attr('d', d3.area().x(d => x(d.day)).y0(d => y(d.lower)).y1(d => y(d.upper)));
  g.append('path').datum(data).attr('fill', 'none').attr('stroke', 'var(--color-red)').attr('stroke-width', 2.25).attr('d', d3.line().x(d => x(d.day)).y(d => y(d.mean)));
  g.append('line').attr('x1', x(0)).attr('x2', x(0)).attr('y1', 0).attr('y2', chartHeight).attr('stroke', 'var(--color-ink)').attr('stroke-dasharray', '4 4');
  g.append('text').attr('class', 'annotation-label').attr('x', x(0) + 6).attr('y', 16).attr('font-size', 11).text('Recession onset');
  g.append('g').attr('transform', \`translate(0,\${chartHeight})\`).call(d3.axisBottom(x).ticks(8));
  g.append('g').call(d3.axisLeft(y).ticks(6));
  finishAxes(g);
  svg.append('text').attr('class', 'axis-label').attr('x', margin.left + chartWidth / 2).attr('y', totalHeight - 28).attr('text-anchor', 'middle').attr('font-size', 12).text('Trading days relative to recession onset');
  svg.append('text').attr('class', 'axis-label').attr('transform', \`translate(20,\${margin.top + chartHeight / 2}) rotate(-90)\`).attr('text-anchor', 'middle').attr('font-size', 12).text('Composite Z-score');
  addSource(svg, margin, totalHeight, 'Data: generated companion event study from manuscript targets.');
}
loadData().then(data => { draw(data); new ResizeObserver(() => draw(data)).observe(document.getElementById('chart')); });`
);

writeHtml(
  "figure-5-recession-episode-heatmap.html",
  "Figure 5: Composite TDA signal by recession episode",
  "Episode heatmap aligned to recession onset.",
  "figure-5-recession-episode-heatmap.json",
  figure5Data,
  `${commonHeader}
function draw(payload) {
  d3.select('#chart').selectAll('*').remove();
  const data = payload.cells;
  const container = document.getElementById('chart');
  const totalWidth = container.clientWidth || 980;
  const totalHeight = Math.max(620, Math.round(totalWidth * 0.58));
  const margin = { top: 76, right: 88, bottom: 76, left: 116 };
  const chartWidth = totalWidth - margin.left - margin.right;
  const chartHeight = totalHeight - margin.top - margin.bottom;
  const svg = d3.select('#chart').append('svg').attr('width', totalWidth).attr('height', totalHeight).attr('role', 'img').attr('aria-labelledby', 'fig-title fig-desc');
  svg.append('title').attr('id', 'fig-title').text('Composite TDA signal by recession episode');
  svg.append('desc').attr('id', 'fig-desc').text('Heatmap rows represent recession episodes and columns represent trading days relative to recession onset.');
  addHeader(svg, margin, 'Composite TDA signal by recession episode', 'Rows are recession episodes; day zero marks onset; generated companion data');
  const g = svg.append('g').attr('transform', \`translate(\${margin.left},\${margin.top})\`);
  const days = Array.from(new Set(data.map(d => d.day))).sort((a, b) => a - b);
  const episodes = payload.episodes;
  const x = d3.scaleBand().domain(days).range([0, chartWidth]).padding(0.01);
  const y = d3.scaleBand().domain(episodes).range([0, chartHeight]).padding(0.08);
  const color = d3.scaleLinear().domain([-3, 0, 3]).range(['#000000', '#F5F5F5', 'var(--color-red)']);
  g.selectAll('.heat-cell').data(data).join('rect').attr('class', 'heat-cell').attr('x', d => x(d.day)).attr('y', d => y(d.episode)).attr('width', x.bandwidth()).attr('height', y.bandwidth()).attr('fill', d => color(d.value)).attr('tabindex', 0).attr('aria-label', d => \`\${d.episode}, day \${d.day}, composite Z \${d.value}\`).on('mouseover focus', (event, d) => showTooltip(event, \`<strong>\${d.episode}</strong><br>Day \${d.day}<br>Composite Z: \${d.value.toFixed(2)}\`)).on('mousemove', moveTooltip).on('mouseout blur', hideTooltip);
  const xLinear = d3.scaleLinear().domain(d3.extent(days)).range([x(days[0]) + x.bandwidth() / 2, x(days[days.length - 1]) + x.bandwidth() / 2]);
  g.append('line').attr('x1', xLinear(0)).attr('x2', xLinear(0)).attr('y1', 0).attr('y2', chartHeight).attr('stroke', 'var(--color-ink)').attr('stroke-dasharray', '4 4');
  g.append('g').attr('transform', \`translate(0,\${chartHeight})\`).call(d3.axisBottom(xLinear).ticks(8));
  g.append('g').call(d3.axisLeft(y));
  finishAxes(g);
  const legend = svg.append('g').attr('transform', \`translate(\${totalWidth - margin.right + 26},\${margin.top + 16})\`);
  const legendScale = d3.scaleLinear().domain([-3, 3]).range([160, 0]);
  const legendAxis = d3.axisRight(legendScale).ticks(5);
  const defs = svg.append('defs');
  const grad = defs.append('linearGradient').attr('id', 'heat-gradient').attr('x1', '0%').attr('x2', '0%').attr('y1', '100%').attr('y2', '0%');
  grad.append('stop').attr('offset', '0%').attr('stop-color', '#000000');
  grad.append('stop').attr('offset', '50%').attr('stop-color', '#F5F5F5');
  grad.append('stop').attr('offset', '100%').attr('stop-color', 'var(--color-red)');
  legend.append('rect').attr('width', 14).attr('height', 160).attr('fill', 'url(#heat-gradient)').attr('stroke', 'var(--color-border)');
  legend.append('g').attr('transform', 'translate(14,0)').call(legendAxis);
  legend.append('text').attr('class', 'axis-label').attr('x', 0).attr('y', -8).attr('font-size', 11).text('Z');
  svg.append('text').attr('class', 'axis-label').attr('x', margin.left + chartWidth / 2).attr('y', totalHeight - 28).attr('text-anchor', 'middle').attr('font-size', 12).text('Trading days relative to recession onset');
  addSource(svg, margin, totalHeight, 'Data: generated companion episode heatmap from manuscript targets.');
}
loadData().then(data => { draw(data); new ResizeObserver(() => draw(data)).observe(document.getElementById('chart')); });`
);

writeHtml(
  "figure-6-roc-curves.html",
  "Figure 6: ROC curves for TDA and baseline recession classifiers",
  "ROC curves comparing TDA and baseline classifiers.",
  "figure-6-roc-curves.json",
  figure6Data,
  `${commonHeader}
function draw(payload) {
  d3.select('#chart').selectAll('*').remove();
  const container = document.getElementById('chart');
  const totalWidth = container.clientWidth || 820;
  const totalHeight = Math.max(640, Math.round(totalWidth * 0.72));
  const margin = { top: 76, right: 40, bottom: 76, left: 78 };
  const chartWidth = totalWidth - margin.left - margin.right;
  const chartHeight = totalHeight - margin.top - margin.bottom;
  const svg = d3.select('#chart').append('svg').attr('width', totalWidth).attr('height', totalHeight).attr('role', 'img').attr('aria-labelledby', 'fig-title fig-desc');
  svg.append('title').attr('id', 'fig-title').text('ROC curves for TDA and baseline recession classifiers');
  svg.append('desc').attr('id', 'fig-desc').text('ROC curves compare true positive and false positive rates for TDA and baseline recession classifiers.');
  addHeader(svg, margin, 'ROC curves for recession classifiers', 'Generated smooth curves from manuscript AUC targets');
  const g = svg.append('g').attr('transform', \`translate(\${margin.left},\${margin.top})\`);
  const x = d3.scaleLinear().domain([0, 1]).range([0, chartWidth]);
  const y = d3.scaleLinear().domain([0, 1]).range([chartHeight, 0]);
  g.append('g').call(d3.axisLeft(y).ticks(6).tickSize(-chartWidth).tickFormat('')).selectAll('line').attr('class', 'gridline').attr('stroke-opacity', 0.55);
  g.select('.domain').remove();
  const colorFor = d => d.role === 'red' ? 'var(--color-red)' : d.role === 'ink' ? 'var(--color-ink)' : d.role === 'secondary' ? '#787878' : d.role === 'random' ? 'var(--color-secondary)' : '#ADADAD';
  const line = d3.line().x(d => x(d.fpr)).y(d => y(d.tpr));
  g.selectAll('.roc-line').data(payload.curves).join('path').attr('class', 'roc-line').attr('fill', 'none').attr('stroke', colorFor).attr('stroke-width', d => d.role === 'red' || d.role === 'ink' ? 2.5 : 1.8).attr('stroke-dasharray', d => d.role === 'random' ? '3 3' : d.role === 'neutral' ? '6 4' : null).attr('d', d => line(d.points));
  g.append('g').attr('transform', \`translate(0,\${chartHeight})\`).call(d3.axisBottom(x).ticks(6).tickFormat(d3.format('.1f')));
  g.append('g').call(d3.axisLeft(y).ticks(6).tickFormat(d3.format('.1f')));
  finishAxes(g);
  const legend = svg.append('g').attr('transform', \`translate(\${margin.left + chartWidth * 0.56},\${margin.top + chartHeight * 0.58})\`);
  const item = legend.selectAll('.legend-item').data(payload.curves).join('g').attr('class', 'legend-item').attr('transform', (d, i) => \`translate(0,\${i * 22})\`);
  item.append('line').attr('x1', 0).attr('x2', 28).attr('y1', 0).attr('y2', 0).attr('stroke', colorFor).attr('stroke-width', 2.2).attr('stroke-dasharray', d => d.role === 'random' ? '3 3' : d.role === 'neutral' ? '6 4' : null);
  item.append('text').attr('class', 'legend-label').attr('x', 36).attr('y', 4).attr('font-size', 12).text(d => \`\${d.label} (AUC=\${d.auc.toFixed(3)})\`);
  svg.append('text').attr('class', 'axis-label').attr('x', margin.left + chartWidth / 2).attr('y', totalHeight - 28).attr('text-anchor', 'middle').attr('font-size', 12).text('False positive rate');
  svg.append('text').attr('class', 'axis-label').attr('transform', \`translate(22,\${margin.top + chartHeight / 2}) rotate(-90)\`).attr('text-anchor', 'middle').attr('font-size', 12).text('True positive rate');
  addSource(svg, margin, totalHeight, 'Data: generated ROC curves from manuscript AUC targets.');
}
loadData().then(data => { draw(data); new ResizeObserver(() => draw(data)).observe(document.getElementById('chart')); });`
);

console.log("Generated data and D3 HTML:");
for (const file of [
  "figure-1-mean-absolute-correlation.html",
  "figure-2-tda-crisis-signals.html",
  "figure-3-lead-cross-correlation.html",
  "figure-4-recession-event-study.html",
  "figure-5-recession-episode-heatmap.html",
  "figure-6-roc-curves.html"
]) {
  console.log(path.join(d3Dir, file));
}
