import urllib.request
import json
import shutil
import os
import re
from datetime import datetime, timezone, timedelta

HTML_FILE  = "index.html"
BACKUP_DIR = "backup"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20viewBox=%270%200%20110%20110%27%3E%3Ctext%20y=%271em%27%20font-size=%2790%27%3E🐱%3C/text%3E%3C/svg%3E">
<meta property="og:title" content="The Sandra Special">
<meta property="og:description" content="2026 March Madness combined Men's + Women's viewing schedule. All channels, all games, all overlap. Built by Carmen Daley.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://thesandraspecial.netlify.app/">
<meta property="og:image" content="https://thesandraspecial.netlify.app/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="The Sandra Special">
<meta name="twitter:image" content="https://thesandraspecial.netlify.app/og-image.png">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>The Sandra Special</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #ffffff; --bg2: #f5f5f3; --bg3: #efefec;
    --text: #1a1a18; --text2: #5a5a56; --text3: #9a9a94;
    --border: rgba(0,0,0,0.12); --border2: rgba(0,0,0,0.22);
    --red: #E24B4A; --win: #1a6e1a; --radius: 8px;
    --wbb: #F47B20; --mbb: #1a6ab5;
    --wbb-bg: #fff8f2; --mbb-bg: #f0f6ff;
    --wbb-border: rgba(244,123,32,0.45); --mbb-border: rgba(26,106,181,0.45);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #1c1c1a; --bg2: #272724; --bg3: #303030;
      --text: #e8e8e2; --text2: #a0a09a; --text3: #606058;
      --border: rgba(255,255,255,0.1); --border2: rgba(255,255,255,0.2);
      --win: #4caf50;
      --wbb-bg: #2a1e10; --mbb-bg: #0f1e30;
      --wbb-border: rgba(244,123,32,0.5); --mbb-border: rgba(26,106,181,0.5);
    }
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); font-size: 14px; padding: 12px 12px 20px; }

  /* ── ROTATE OVERLAY ── */
  #rotateOverlay {
    display: none;
    position: fixed; inset: 0; z-index: 9999;
    background: #111;
    flex-direction: column;
    align-items: center; justify-content: center;
    gap: 16px; color: #eee; text-align: center; padding: 24px;
  }
  #rotateOverlay.show { display: flex; }
  .rotate-icon { font-size: 52px; animation: spin 2s ease-in-out infinite; transform-origin: center; }
  @keyframes spin { 0%,100%{transform:rotate(-15deg)} 50%{transform:rotate(15deg)} }
  #rotateOverlay p { font-size: 14px; line-height: 1.6; max-width: 260px; color: #bbb; }
  #rotateOverlay strong { color: #fff; font-size: 16px; display: block; margin-bottom: 4px; }
  #rotateSkip { margin-top: 8px; padding: 10px 24px; border: 1.5px solid #555; border-radius: 20px; background: transparent; color: #999; font-size: 12px; cursor: pointer; font-family: inherit; }

  /* ── HEADER ── */
  .header-row { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; flex-wrap: wrap; }
  h1 { font-size: 21px; font-family:'Bebas Neue',sans-serif; letter-spacing:0.04em; white-space:nowrap; }
  .wbb-accent { color: var(--wbb); }
  .mbb-accent { color: var(--mbb); }
  .subtitle { font-size: 11px; color: var(--text3); margin-bottom: 10px; }

  /* ── FILTER TOGGLE ── */
  .filter-strip { display: flex; gap: 5px; margin-bottom: 10px; }
  .filter-btn { padding: 4px 12px; border-radius: 14px; border: 1.5px solid var(--border2); background: transparent; color: var(--text2); cursor: pointer; font-size: 11px; font-weight: 600; font-family: inherit; transition: all .15s; }
  .filter-btn.active-both { background: var(--text); color: var(--bg); border-color: var(--text); }
  .filter-btn.active-wbb { background: var(--wbb); color: #fff; border-color: var(--wbb); }
  .filter-btn.active-mbb { background: var(--mbb); color: #fff; border-color: var(--mbb); }

  /* ── DAY TABS ── */
  .day-tabs { display: flex; gap: 5px; flex-wrap: wrap; margin-bottom: 10px; }
  .day-btn { padding: 5px 11px; border-radius: 20px; border: 1px solid var(--border2); background: transparent; color: var(--text2); cursor: pointer; font-size: 11px; line-height: 1.4; text-align: center; font-family: inherit; transition: all .15s; }
  .day-btn.active { background: var(--text); color: var(--bg); border-color: var(--text); }
  .day-btn.today { box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--text); font-weight: 700; }
  .day-btn.today.active { box-shadow: 0 0 0 2px var(--bg), 0 0 0 4px var(--text); }
  .day-btn.has-wbb { border: 3px solid var(--wbb); }
  .day-btn.has-mbb { border: 3px solid var(--mbb); }
  .day-btn.has-both {
    border: 3px solid transparent;
    background-image: linear-gradient(var(--bg), var(--bg)), linear-gradient(to right, var(--wbb) 50%, var(--mbb) 50%);
    background-origin: border-box;
    background-clip: padding-box, border-box;
  }
  .day-btn.active.has-wbb { background: var(--wbb); color: #fff; border-color: var(--wbb); }
  .day-btn.active.has-mbb { background: var(--mbb); color: #fff; border-color: var(--mbb); }
  .day-btn.active.has-both { background-image: linear-gradient(to right, var(--wbb) 50%, var(--mbb) 50%); background-origin: padding-box; background-clip: padding-box; color: #fff; border-color: transparent; }

  /* ── STICKY HEADER ── */
  .sticky-day { position: sticky; top: var(--header-h, 90px); z-index: 30; background: var(--bg); padding: 6px 0 5px; display: flex; flex-direction: column; gap: 2px; border-bottom: 1px solid var(--border); margin-bottom: 10px; }
  .sticky-day-row { display: flex; align-items: center; gap: 8px; }
  .sticky-day-summary { font-size: 11px; color: var(--text2); padding: 0 2px 2px; }
  .sticky-day-pill { display: inline-flex; align-items: center; gap: 6px; background: var(--bg3); border: 1px solid var(--border2); border-radius: 20px; padding: 3px 10px; }
  .sticky-day-label { font-size: 11px; font-weight: 700; color: var(--text); }
  .sticky-round-label { font-size: 10px; color: var(--text2); }

  /* ── NAV ARROWS ── */
  .nav-arrow { position: fixed; top: 50%; transform: translateY(-50%); z-index: 50; width: 28px; height: 56px; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.12); color: rgba(255,255,255,0.7); font-size: 20px; font-weight: 300; border-radius: 4px; cursor: pointer; user-select: none; border: none; font-family: inherit; padding: 0; }
  .nav-arrow.left { left: 0; border-radius: 0 4px 4px 0; }
  .nav-arrow.right { right: 0; border-radius: 4px 0 0 4px; }
  .nav-arrow:active { background: rgba(0,0,0,0.25); }
  @media (prefers-color-scheme: dark) {
    .nav-arrow { background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.5); }
  }

  /* ── BANNERS ── */
  .overlap-note { font-size: 11px; color: var(--text2); margin-bottom: 10px; padding: 7px 12px; background: var(--bg2); border-left: 3px solid var(--border2); border-radius: 0 var(--radius) var(--radius) 0; display: none; }
  .cinderella-banner { font-size: 10px; color: #7c3aed; margin-bottom: 10px; padding: 7px 12px; background: #f5f3ff; border-left: 3px solid #7c3aed; border-radius: 0 var(--radius) var(--radius) 0; display: none; }
  @media (prefers-color-scheme: dark) { .cinderella-banner { background: #1e1040; } }
  .tbd-banner { display:none; font-size:11px; color:var(--text2); margin-bottom:10px; padding:7px 12px; background:var(--bg2); border-left:3px solid #f59e0b; border-radius:0 var(--radius) var(--radius) 0; font-style:italic; }

  /* ── LEGEND ── */
  .legend { display: flex; gap: 12px; margin-bottom: 10px; font-size: 10px; color: var(--text2); flex-wrap: wrap; align-items: center; }
  .legend-dot { width: 10px; height: 10px; border-radius: 2px; flex-shrink: 0; display: inline-block; }
  .legend-item { display: flex; align-items: center; gap: 4px; }

  /* ── GRID ── */
  .grid-wrap { width: 100%; }
  .grid-header { display: flex; position: sticky; top: var(--sticky-h, 42px); z-index: 19; }
  .corner { flex-shrink: 0; font-size: 10px; color: var(--text3); padding: 5px 6px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); background: var(--bg2); display: flex; align-items: flex-end; }
  .ch-head { flex: 1; font-size: 11px; font-weight: 600; color: var(--text2); text-align: center; padding: 5px 4px; border-bottom: 1px solid var(--border); border-right: 1px solid var(--border); background: var(--bg2); white-space: nowrap; }
  .ch-head.wbb-ch { color: var(--wbb); }
  .ch-head.mbb-ch { color: var(--mbb); }
  .ch-head:last-child { border-right: none; }
  .grid-body { display: flex; position: relative; }
  .time-col { flex-shrink: 0; position: relative; border-right: 1px solid var(--border); }
  .time-label { position: absolute; font-size: 9px; color: var(--text3); right: 5px; white-space: nowrap; transform: translateY(-50%); }

  /* ── GAME BARS ── */
  .game-bar { position: absolute; left: 3px; right: 3px; border-radius: 5px; padding: 4px 6px; display: flex; flex-direction: column; justify-content: flex-start; overflow: hidden; background: var(--bg2); border: 1px solid var(--border2); }
  .game-bar.wbb-bar { background: var(--wbb-bg); border: 1.5px solid var(--wbb-border); }
  .game-bar.mbb-bar { background: var(--mbb-bg); border: 1.5px solid var(--mbb-border); }
  /* Upset: dotted gender-colored border + very faint diagonal stripes layered under gender background */
  .game-bar.wbb-bar.upset {
    border: 2.5px dotted var(--wbb);
    background-image: repeating-linear-gradient(
      45deg,
      transparent,
      transparent 5px,
      rgba(244,123,32,0.08) 5px,
      rgba(244,123,32,0.08) 6px
    );
  }
  .game-bar.mbb-bar.upset {
    border: 2.5px dotted var(--mbb);
    background-image: repeating-linear-gradient(
      45deg,
      transparent,
      transparent 5px,
      rgba(26,106,181,0.08) 5px,
      rgba(26,106,181,0.08) 6px
    );
  }
  @media (prefers-color-scheme: dark) {
    .game-bar.wbb-bar.upset {
      background-image: repeating-linear-gradient(
        45deg,
        transparent,
        transparent 5px,
        rgba(244,123,32,0.12) 5px,
        rgba(244,123,32,0.12) 6px
      );
    }
    .game-bar.mbb-bar.upset {
      background-image: repeating-linear-gradient(
        45deg,
        transparent,
        transparent 5px,
        rgba(26,106,181,0.14) 5px,
        rgba(26,106,181,0.14) 6px
      );
    }
  }
  .bar-pod { font-size: 8px; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-team { font-size: 9px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; line-height: 1.4; color: var(--text); display: flex; align-items: center; gap: 3px; }
  .bar-team.winner { color: var(--win); font-weight: 700; }
  .bar-team.loser { color: var(--text3); }
  .upset-label { font-size: 8px; font-weight: 800; color: var(--text2); letter-spacing: .06em; margin-top: 2px; text-transform: uppercase; }
  .bar-score-line { font-size: 10px; font-weight: 700; color: var(--text); margin-top: 2px; white-space: nowrap; }
  .bar-venue { font-size: 8px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: var(--text3); margin-top: 1px; }
  .bar-link { font-size: 7px; color: var(--text3); margin-top: auto; padding-top: 2px; text-align: right; opacity: 0.65; }
  .game-bar:hover .bar-link, .game-bar:active .bar-link { opacity: 1; color: var(--wbb); }
  .game-bar.mbb-bar:hover .bar-link, .game-bar.mbb-bar:active .bar-link { color: var(--mbb); }

  .team-logo { width: 12px; height: 12px; object-fit: contain; flex-shrink: 0; }
  .cinderella-label { font-size: 8px; font-weight: 700; color: #7c3aed; letter-spacing: .04em; margin-top: 1px; }

  .now-line { position: absolute; left: 0; right: 0; height: 2px; background: var(--red); opacity: 0.8; z-index: 10; pointer-events: none; }
  .now-label { position: absolute; left: 0; top: -13px; font-size: 8px; font-weight: 700; color: var(--red); white-space: nowrap; background: var(--bg); padding: 0 3px; border-radius: 3px; letter-spacing: .04em; }

  /* region colors */
  .r-FW1, .r-FW3 { color: #b03030; }
  .r-SAC2, .r-SAC4 { color: #1a5fa0; }
  .r-F4 { color: #5040b0; }
  @media (prefers-color-scheme: dark) {
    .r-FW1, .r-FW3 { color: #f09090; }
    .r-SAC2, .r-SAC4 { color: #80b8f0; }
    .r-F4 { color: #b0a0f8; }
  }

  /* ── CHANNEL DIVIDER LABELS ── */
  .ch-divider { position: absolute; top: 0; bottom: 0; z-index: 5; pointer-events: none; }
  .ch-divider-line { position: absolute; top: 0; bottom: 0; width: 2px; background: var(--border); }
  .ch-section-label { writing-mode: vertical-rl; font-size: 8px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; opacity: 0.35; position: absolute; top: 8px; }

  /* ── GUIDE MODAL ── */
  .guide-modal { display: none; position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 100; background: rgba(0,0,0,0.55); }
  .guide-modal.open { display: flex; align-items: center; justify-content: center; }
  .guide-content { background: var(--bg); border-radius: 12px; padding: 20px; max-width: 380px; width: 90%; max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }
  .guide-content h2 { font-size: 15px; font-weight: 700; color: var(--wbb); margin-bottom: 12px; }
  .guide-item { display: flex; gap: 10px; align-items: flex-start; margin-bottom: 12px; font-size: 12px; line-height: 1.4; }
  .guide-icon { font-size: 16px; flex-shrink: 0; width: 24px; text-align: center; }
  .guide-close { width: 100%; padding: 10px; margin-top: 8px; border-radius: 8px; border: none; background: var(--wbb); color: white; font-size: 13px; font-weight: 600; cursor: pointer; font-family: inherit; }

  /* ── FUTURE NOTE ── */
  .future-note { font-size: 12px; color: var(--text2); padding: 24px 0; text-align: center; font-style: italic; line-height: 1.8; }

  /* ── MOBILE ── */
  @media (max-width: 600px) {
    body { padding: 8px; }
    .day-btn { font-size: 9px; padding: 3px 7px; }
    .bar-team { font-size: 7.5px; }
    .bar-pod { font-size: 7px; }
    .bar-score-line { font-size: 7px; }
    .bar-venue { display: none; }
    .team-logo { width: 10px; height: 10px; }
    .ch-head { font-size: 9px; padding: 4px 2px; }
  }
</style>
</head>
<body>

<!-- Rotate overlay for portrait mobile -->
<div id="rotateOverlay">
  <div class="rotate-icon">📱</div>
  <div>
    <strong>Rotate for the full picture</strong>
    <p>This guide works best in landscape mode — 9 channels is a lot to show on a portrait screen!</p>
  </div>
  <button id="rotateSkip" onclick="document.getElementById('rotateOverlay').classList.remove('show');localStorage.setItem('skipRotate','1')">View anyway</button>
</div>

<!-- PERSISTENT HEADER -->
<div style="position:sticky;top:0;z-index:40;background:var(--bg);padding-bottom:6px;border-bottom:1px solid var(--border);margin-bottom:8px;">
  <div class="header-row">
    <span style="font-size:20px">🏀</span>
    <h1><span class="wbb-accent">W</span> + <span class="mbb-accent">M</span> MADNESS</h1>
    <button onclick="document.getElementById('guideOverlay').classList.add('open')" style="background:none;border:2px solid var(--wbb);color:var(--wbb);border-radius:50%;width:22px;height:22px;font-size:12px;font-weight:800;cursor:pointer;padding:0;line-height:1;flex-shrink:0;margin-left:4px;">?</button>
    <span style="margin-left:auto;font-size:10px;color:var(--text3)">Passion project by <a href="https://www.linkedin.com/in/carmendaley/" target="_blank" style="color:var(--text2);text-decoration:none;border-bottom:1px solid var(--border2);">Carmen Daley</a></span>
  </div>
  <p class="subtitle" id="tzSubtitle">All times Eastern · Tap a day to navigate</p>
  <!-- FILTER TOGGLE -->
  <div class="filter-strip">
    <button class="filter-btn active-both" id="filterBoth" onclick="setFilter('both')">Both</button>
    <button class="filter-btn" id="filterWBB" onclick="setFilter('wbb')">⛹🏿‍♀️ Women's only</button>
    <button class="filter-btn" id="filterMBB" onclick="setFilter('mbb')">⛹🏽‍♂️ Men's only</button>
  </div>
</div>

<!-- DAY TABS -->
<div style="position:relative;display:flex;align-items:center;gap:4px">
  <button class="nav-arrow left" id="navLeft" onclick="navStep(-1)" aria-label="Previous day">&#8249;</button>
  <button class="nav-arrow right" id="navRight" onclick="navStep(1)" aria-label="Next day">&#8250;</button>
  <div class="day-tabs" id="dayTabs" style="flex:1;min-width:0"></div>
</div>

<!-- STICKY DAY HEADER -->
<div class="sticky-day" id="stickyDay">
  <div class="sticky-day-row">
    <a href="https://www.espn.com/womens-college-basketball/bracket" target="_blank" style="font-size:12px;font-family:'Bebas Neue',sans-serif;letter-spacing:0.04em;color:var(--wbb);margin-right:4px;white-space:nowrap;flex-shrink:0;text-decoration:none;">WBB Bracket ↗</a>
    <a href="https://www.espn.com/mens-college-basketball/bracket" target="_blank" style="font-size:12px;font-family:'Bebas Neue',sans-serif;letter-spacing:0.04em;color:var(--mbb);margin-right:8px;white-space:nowrap;flex-shrink:0;text-decoration:none;">MBB Bracket ↗</a>
    <div class="sticky-day-pill"><span class="sticky-day-label" id="stickyDayLabel"></span></div>
  </div>
  <div class="sticky-day-summary" id="daySummary"></div>
</div>

<!-- BANNERS -->
<div class="overlap-note" id="overlapNote"></div>
<div class="tbd-banner" id="tbdBanner"></div>
<div class="cinderella-banner" id="cinderellaBanner"></div>
<!-- GUIDE MODAL -->
<div class="guide-modal" id="guideOverlay" onclick="if(event.target===this)this.classList.remove('open')">
  <div class="guide-content">
    <h2>🏀 How to use this page</h2>
    <div class="guide-item"><span class="guide-icon">📱</span><div><strong>Landscape mode recommended on mobile</strong> — 9 channels is a lot. Rotate your phone for the best experience.</div></div>
    <div class="guide-item"><span class="guide-icon">🎛️</span><div><strong>Filter toggle</strong> — switch between Both, Women's only, or Men's only to de-clutter the view.</div></div>
    <div class="guide-item"><span class="guide-icon">📅</span><div><strong>Tabs</strong> — tap any date to see that day's games. Swipe left/right to move between days.</div></div>
    <div class="guide-item"><span class="guide-icon">📺</span><div><strong>Columns</strong> — each column is a TV channel. Games are placed by start time so you can see exactly what overlaps.</div></div>
    <div class="guide-item"><span class="guide-icon">↗</span><div><strong>Tap any game bar</strong> — opens the ESPN game page for live scores and stats.</div></div>
    <div class="guide-item"><span class="guide-icon">🕐</span><div><strong>Timezones</strong> — times adjust to your local timezone automatically.</div></div>
    <div class="guide-item"><span class="guide-icon">🔴</span><div><strong>Red line = NOW</strong> — shows current time on today's view.</div></div>
    <div class="guide-item"><span class="guide-icon">🟢</span><div><strong>Green = winner</strong> — completed games show the winning team in green with the final score.</div></div>
    <div class="guide-item"><span class="guide-icon">✨</span><div><strong>Cinderella</strong> — sparkle wand next to teams that reached the Sweet 16 as a #10 seed or lower.</div></div>
    <div class="guide-item"><span class="guide-icon">🫧</span><div><strong>Bubble team</strong> — blue bubbles next to teams that had to win a First Four game just to make the tournament.</div></div>
    <div style="border-top:1px solid var(--border);margin:10px 0 12px"></div>
    <div style="font-size:11px;font-weight:700;color:var(--text);margin-bottom:8px;">Game bar colors</div>
    <div class="guide-item"><span class="guide-icon">🟠</span><div><strong>Orange bars</strong> — Women's tournament (WBB) on ESPN, ABC, ESPN2, ESPNU, ESPNews.</div></div>
    <div class="guide-item"><span class="guide-icon">🔵</span><div><strong>Blue bars</strong> — Men's tournament (MBB) on CBS, TBS, TNT, truTV.</div></div>
    <div style="border-top:1px solid var(--border);margin:10px 0 12px"></div>
    <div style="font-size:11px;font-weight:700;color:var(--text);margin-bottom:8px;">Date tab borders</div>
    <div class="guide-item"><span style="display:inline-block;width:32px;height:18px;border-radius:10px;border:3px solid var(--wbb);flex-shrink:0"></span><div>Orange — Women's games only that day.</div></div>
    <div class="guide-item"><span style="display:inline-block;width:32px;height:18px;border-radius:10px;border:3px solid var(--mbb);flex-shrink:0"></span><div>Blue — Men's games only that day.</div></div>
    <div class="guide-item"><span style="display:inline-block;width:32px;height:18px;border-radius:10px;border:3px solid transparent;background-image:linear-gradient(var(--bg),var(--bg)),linear-gradient(to right,var(--wbb) 50%,var(--mbb) 50%);background-origin:border-box;background-clip:padding-box,border-box;flex-shrink:0"></span><div>Split orange/blue — both tournaments playing that day.</div></div>
    <div class="guide-item"><span style="display:inline-block;width:32px;height:18px;border-radius:10px;border:3px solid var(--mbb);box-shadow:0 0 0 2px var(--bg),0 0 0 4px var(--text);flex-shrink:0"></span><div><strong>Bold outer ring</strong> — today's date.</div></div>
    <button class="guide-close" onclick="document.getElementById('guideOverlay').classList.remove('open')">Got it!</button>
  </div>
</div>

<!-- GRID CONTAINER -->
<div id="gridContainer"></div>

<script>
// ─────────────────────────────────────────────
// CONSTANTS
// ─────────────────────────────────────────────
const DURATION = 120;
const PX_PER_MIN = 1.0;
const TIME_COL_W = 44;

// All channels — WBB first, then MBB
const WBB_NETS = ["ESPN","ABC","ESPN2","ESPNU","ESPNews"];
const MBB_NETS = ["CBS","TBS","TNT","truTV"];
const ALL_NETS  = [...WBB_NETS, ...MBB_NETS];

// Current filter
let activeFilter = 'both'; // 'both' | 'wbb' | 'mbb'

function setFilter(f) {
  activeFilter = f;
  document.getElementById('filterBoth').className = 'filter-btn' + (f==='both'?' active-both':'');
  document.getElementById('filterWBB').className  = 'filter-btn' + (f==='wbb'?' active-wbb':'');
  document.getElementById('filterMBB').className  = 'filter-btn' + (f==='mbb'?' active-mbb':'');
  render();
}

// ─────────────────────────────────────────────
// WOMEN'S GAME DATA  (gender:"W")
// ─────────────────────────────────────────────
const G_WBB = [
%%WBB_DATA%%
].map(g => ({...g, gender:"W"}));

// ─────────────────────────────────────────────
// MEN'S GAME DATA  (gender:"M")
// ─────────────────────────────────────────────
const G_MBB = [
%%MBB_DATA%%
].map(g => ({...g, gender:"M"}));

// ─────────────────────────────────────────────
// COMBINED SCHEDULE
// ─────────────────────────────────────────────
const G = [...G_WBB, ...G_MBB];

const ALL_DAY_ORDER = ["Tue Mar 17","Wed Mar 18","Thu Mar 19","Fri Mar 20","Sat Mar 21","Sun Mar 22","Mon Mar 23","Thu Mar 26","Fri Mar 27","Sat Mar 28","Sun Mar 29","Mon Mar 30","Fri Apr 3","Sat Apr 4","Sun Apr 5","Mon Apr 6"];
const days = ALL_DAY_ORDER.filter(d => G.some(g => g.day === d));

const roundMap = {
  "Tue Mar 17":"First4","Wed Mar 18":"First4",
  "Thu Mar 19":"R1","Fri Mar 20":"R1",
  "Sat Mar 21":"R2","Sun Mar 22":"R2",
  "Mon Mar 23":"R2",
  "Thu Mar 26":"S16","Fri Mar 27":"S16",
  "Sat Mar 28":"E8","Sun Mar 29":"E8",
  "Mon Mar 30":"E8",
  "Fri Apr 3":"Semi","Sat Apr 4":"Semi",
  "Sun Apr 5":"Champ","Mon Apr 6":"Champ"
};

const WBB_ROUND = {
  "Wed Mar 18":"First4","Thu Mar 19":"First4",
  "Fri Mar 20":"R1","Sat Mar 21":"R1",
  "Sun Mar 22":"R2","Mon Mar 23":"R2",
  "Fri Mar 27":"S16","Sat Mar 28":"S16",
  "Sun Mar 29":"E8","Mon Mar 30":"E8",
  "Fri Apr 3":"Semi","Sun Apr 5":"Champ",
};
const MBB_ROUND = {
  "Tue Mar 17":"First4","Wed Mar 18":"First4",
  "Thu Mar 19":"R1","Fri Mar 20":"R1",
  "Sat Mar 21":"R2","Sun Mar 22":"R2",
  "Thu Mar 26":"S16","Fri Mar 27":"S16",
  "Sat Mar 28":"E8","Sun Mar 29":"E8",
  "Sat Apr 4":"Semi","Mon Apr 6":"Champ",
};
function getRoundLabel(day, gender){
  return gender==='W' ? (WBB_ROUND[day]||'') : (MBB_ROUND[day]||'');
}

const SWEET16_DAYS = new Set(["Fri Mar 27","Sat Mar 28","Thu Mar 26"]);
const ELITE8_DAYS  = new Set(["Sun Mar 29","Mon Mar 30","Sat Mar 28","Sun Mar 29"]);
const FINAL4_DAYS  = new Set(["Fri Apr 3","Sat Apr 4","Sun Apr 5","Mon Apr 6"]);
const deepRunDays  = new Set([...SWEET16_DAYS,...ELITE8_DAYS,...FINAL4_DAYS]);

function getCinderellaTeams(){
  const c = new Map();
  G.forEach(g=>{
    if(!deepRunDays.has(g.day))return;
    const am=g.away.match(/^[(]([0-9]+)[)]/);
    const hm=g.home.match(/^[(]([0-9]+)[)]/);
    if(am&&parseInt(am[1])>=10){
      const bare=g.away.replace(/^[(][0-9]+[)] */,"");
      const key=bare+"|"+g.gender;
      if(!c.has(key)) c.set(key,{gender:g.gender,logo:g.awayLogo,seeded:g.away,bare});
    }
    if(hm&&parseInt(hm[1])>=10){
      const bare=g.home.replace(/^[(][0-9]+[)] */,"");
      const key=bare+"|"+g.gender;
      if(!c.has(key)) c.set(key,{gender:g.gender,logo:g.homeLogo,seeded:g.home,bare});
    }
  });
  return c;
}
const cinderellaTeams = getCinderellaTeams();
function isCinderella(t){
  const bare=t.replace(/^[(][0-9]+[)] */,"");
  // Check both genders — used for wand SVG on game bars where we have gender context separately
  return cinderellaTeams.has(bare+"|W")||cinderellaTeams.has(bare+"|M");
}

const FIRST_FOUR_DAYS = new Set(["Tue Mar 17","Wed Mar 18"]);
function getBubbleTeams(){
  // Keys on bareName|gender so MBB bubble teams don't bleed into WBB and vice versa
  const w=new Set();
  G.forEach(g=>{
    if(!FIRST_FOUR_DAYS.has(g.day)||g.status!=="final")return;
    const ab=g.away.replace(/^[(][0-9]+[)] */,"");
    const hb=g.home.replace(/^[(][0-9]+[)] */,"");
    if(g.ascore>g.hscore)w.add(ab+"|"+g.gender);
    else if(g.hscore>g.ascore)w.add(hb+"|"+g.gender);
  });
  return w;
}
const bubbleTeams = getBubbleTeams();
function isBubbleForDay(t,gender,d){
  return bubbleTeams.has(t.replace(/^[(][0-9]+[)] */,"")+"|"+gender)&&!FIRST_FOUR_DAYS.has(d);
}

// ─────────────────────────────────────────────
// TIMEZONE
// ─────────────────────────────────────────────
const _userTZ = Intl.DateTimeFormat().resolvedOptions().timeZone;
const US_TZ_MAP = {
  'America/New_York':{name:'Eastern Time',abbr:'ET',etDiff:0},
  'America/Detroit':{name:'Eastern Time',abbr:'ET',etDiff:0},
  'America/Indiana/Indianapolis':{name:'Eastern Time',abbr:'ET',etDiff:0},
  'America/Kentucky/Louisville':{name:'Eastern Time',abbr:'ET',etDiff:0},
  'America/Chicago':{name:'Central Time',abbr:'CT',etDiff:-1},
  'America/Indiana/Knox':{name:'Central Time',abbr:'CT',etDiff:-1},
  'America/Menominee':{name:'Central Time',abbr:'CT',etDiff:-1},
  'America/Denver':{name:'Mountain Time',abbr:'MT',etDiff:-2},
  'America/Boise':{name:'Mountain Time',abbr:'MT',etDiff:-2},
  'America/Phoenix':{name:'Mountain Time',abbr:'MT',etDiff:-2},
  'America/Los_Angeles':{name:'Pacific Time',abbr:'PT',etDiff:-3},
  'America/Anchorage':{name:'Alaska Time',abbr:'AKT',etDiff:-4},
  'America/Juneau':{name:'Alaska Time',abbr:'AKT',etDiff:-4},
  'Pacific/Honolulu':{name:'Hawaii Time',abbr:'HT',etDiff:-6},
};
const _tzInfo = US_TZ_MAP[_userTZ]||null;
const _isET   = _tzInfo?_tzInfo.abbr==='ET':false;
const _isUS   = !!_tzInfo;
const _tzLabel = _tzInfo?_tzInfo.name:'Eastern Time';

function toLocalTime(etStr){
  if(!etStr||etStr==='TBD'||etStr==='12:00 AM')return etStr;
  if(!_isUS||_isET)return etStr;
  const[hm,ap]=etStr.split(' ');let[h,m]=hm.split(':').map(Number);
  if(ap==='PM'&&h!==12)h+=12;if(ap==='AM'&&h===12)h=0;
  let lh=h+_tzInfo.etDiff;if(lh<0)lh+=24;if(lh>=24)lh-=24;
  const lap=lh>=12?'PM':'AM';let h12=lh>12?lh-12:(lh===0?12:lh);
  return h12+(m>0?':'+String(m).padStart(2,'0'):'')+' '+lap;
}
function toLocalMin(etStr){
  if(!etStr||etStr==='TBD'||etStr==='12:00 AM')return null;
  const local=toLocalTime(etStr);if(!local||local==='TBD'||local==='12:00 AM')return null;
  const[hm,ap]=local.split(' ');
  const parts=hm.split(':');
  let h=Number(parts[0]),m=parts.length>1?Number(parts[1]):0;
  if(ap==='PM'&&h!==12)h+=12;if(ap==='AM'&&h===12)h=0;
  return h*60+m;
}
// toMin removed — use toLocalMin everywhere for consistency

const _tzSubEl=document.getElementById('tzSubtitle');
if(_tzSubEl){
  if(!_isUS)_tzSubEl.textContent='Times in Eastern Time — non-US timezone, defaulting to ET';
  else if(_isET)_tzSubEl.textContent='All times Eastern · Tap a day to navigate';
  else _tzSubEl.textContent='Times in your local timezone ('+_tzInfo.name+') · Tap a day to navigate';
}

// ─────────────────────────────────────────────
// ROTATE OVERLAY LOGIC
// ─────────────────────────────────────────────
function checkRotate(){
  if(localStorage.getItem('skipRotate'))return;
  const portrait = window.innerHeight > window.innerWidth;
  const mobile   = window.innerWidth < 768;
  const el = document.getElementById('rotateOverlay');
  if(el) el.classList.toggle('show', portrait && mobile);
}
window.addEventListener('orientationchange',()=>setTimeout(checkRotate,200));
window.addEventListener('resize', checkRotate);
checkRotate();

// ─────────────────────────────────────────────
// TAB & STATE
// ─────────────────────────────────────────────
const now0=new Date();
const todayStr=now0.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"}).replace(",","");
const todayDay=days.find(d=>d===todayStr)||days[0];
let activeDay=todayDay;

function buildTabs(){
  const c=document.getElementById("dayTabs");
  days.forEach(d=>{
    const hasW = G.some(g=>g.day===d&&g.gender==='W');
    const hasM = G.some(g=>g.day===d&&g.gender==='M');
    const genderCls = (hasW&&hasM)?'has-both':hasW?'has-wbb':'has-mbb';
    const b=document.createElement("button");
    b.className="day-btn "+genderCls+(d===activeDay?" active":"")+(d===todayDay?" today":"");
    b.innerHTML=d;
    b.onclick=()=>{activeDay=d;document.querySelectorAll(".day-btn").forEach(x=>x.classList.remove("active"));b.classList.add("active");render();updateNavArrows();};
    c.appendChild(b);
  });
}

// ─────────────────────────────────────────────
// WATCH PARTY DATA (Philly)
// ─────────────────────────────────────────────
// ─────────────────────────────────────────────
// RENDER
// ─────────────────────────────────────────────
const WBB_ROUND_INFO = {
  "Sun Mar 22":{total:8,partner:"Mon Mar 23",partnerShort:"the 23rd",round:"WBB Second Round"},
  "Mon Mar 23":{total:8,partner:"Sun Mar 22",partnerShort:"the 22nd",round:"WBB Second Round"},
  "Fri Mar 27":{total:4,partner:"Sat Mar 28",partnerShort:"the 28th",round:"WBB Sweet 16"},
  "Sat Mar 28":{total:4,partner:"Fri Mar 27",partnerShort:"the 27th",round:"WBB Sweet 16"},
  "Sun Mar 29":{total:2,partner:null,partnerShort:null,round:"WBB Elite Eight"},
  "Mon Mar 30":{total:2,partner:null,partnerShort:null,round:"WBB Elite Eight"},
  "Fri Apr 3":{total:2,partner:null,partnerShort:null,round:"WBB Final Four"},
  "Sun Apr 5":{total:1,partner:null,partnerShort:null,round:"WBB Championship"},
};
const MBB_ROUND_INFO = {
  "Sat Mar 21":{total:8,partner:"Sun Mar 22",partnerShort:"the 22nd",round:"MBB Second Round"},
  "Sun Mar 22":{total:8,partner:"Sat Mar 21",partnerShort:"the 21st",round:"MBB Second Round"},
  "Thu Mar 26":{total:4,partner:"Fri Mar 27",partnerShort:"the 27th",round:"MBB Sweet 16"},
  "Fri Mar 27":{total:4,partner:"Thu Mar 26",partnerShort:"the 26th",round:"MBB Sweet 16"},
  "Sat Mar 28":{total:2,partner:null,partnerShort:null,round:"MBB Elite Eight"},
  "Sun Mar 29":{total:2,partner:null,partnerShort:null,round:"MBB Elite Eight"},
  "Sat Apr 4":{total:2,partner:null,partnerShort:null,round:"MBB Final Four"},
  "Mon Apr 6":{total:1,partner:null,partnerShort:null,round:"MBB Championship"},
};

function render(){
  let allGames = G.filter(g=>g.day===activeDay);
  // Apply filter
  if(activeFilter==='wbb') allGames = allGames.filter(g=>g.gender==='W');
  if(activeFilter==='mbb') allGames = allGames.filter(g=>g.gender==='M');

  const container = document.getElementById("gridContainer");
  const note      = document.getElementById("overlapNote");
  note.style.display = "none";

  document.getElementById("stickyDayLabel").textContent = "Viewing "+(activeDay===todayDay?"TODAY":activeDay);

  // Cinderella banner
  const cinBanner = document.getElementById("cinderellaBanner");
  const daycins = [...cinderellaTeams.entries()].filter(([key, info])=>
    allGames.some(g=>g.gender===info.gender&&(g.away.includes(info.bare)||g.home.includes(info.bare)))
  );
  if(daycins.length){
    cinBanner.style.display="block";
    const items = daycins.map(([key, info])=>{
      const gColor = info.gender==='W' ? 'var(--wbb)' : 'var(--mbb)';
      const gLabel = info.gender==='W' ? 'WBB' : 'MBB';
      const badge = "<span style='font-size:9px;font-weight:800;color:"+gColor+";border:1.5px solid "+gColor+";border-radius:4px;padding:1px 4px;margin-right:5px;white-space:nowrap'>"+gLabel+"</span>";
      const logo = info.logo ? "<img src='"+info.logo+"' style='width:14px;height:14px;object-fit:contain;vertical-align:middle;margin-right:3px'>" : "";
      return badge+logo+"<span style='font-weight:600'>"+info.seeded+"</span> still dancing!";
    });
    cinBanner.innerHTML = "<b>✨ Cinderella"+(daycins.length>1?" alerts":" alert")+"</b> — "+items.join(" &nbsp;·&nbsp; ");
  } else { cinBanner.style.display="none"; }

  // TBD banner
  const tbdBanner = document.getElementById("tbdBanner");
  const tbdLines = [];
  [["W", WBB_ROUND_INFO], ["M", MBB_ROUND_INFO]].forEach(([gender, INFO])=>{
    const roundInfo = INFO[activeDay];
    if(!roundInfo) return;
    const todayGames = G.filter(g=>g.day===activeDay&&g.gender===gender);
    const todayWithTime = todayGames.filter(g=>toLocalMin(g.time)!==null).length;
    const todayTBD = todayGames.length - todayWithTime;
    if(todayTBD === 0) return;
    const partnerDay = roundInfo.partner;
    const partnerGames = partnerDay ? G.filter(g=>g.day===partnerDay&&g.gender===gender) : [];
    const partnerWithTime = partnerGames.filter(g=>toLocalMin(g.time)!==null).length;
    let blurb = "";
    if(todayWithTime===0 && partnerWithTime===0){
      if(partnerDay){
        blurb = roundInfo.total+" "+roundInfo.round+" games split between "+activeDay+" and "+roundInfo.partnerShort+" — which ones air on which day is TBD!";
      } else {
        blurb = roundInfo.total+" "+roundInfo.round+(roundInfo.total===1?" game":" games")+" — matchups TBD after previous round.";
      }
    } else {
      blurb = todayTBD+" more "+roundInfo.round+" game"+(todayTBD===1?"":"s")+" on "+activeDay+" TBD — check back for the full slate.";
    }
    const noTimeGames = todayGames.filter(g=>toLocalMin(g.time)===null&&(g.away!=="TBD"||g.home!=="TBD"));
    if(noTimeGames.length){
      const rows = noTimeGames.map(g=>{
        const a = g.away==="TBD"?"TBD":(g.awayShort||g.away);
        const h = g.home==="TBD"?"TBD":(g.homeShort||g.home);
        const pod = g.reg||"";
        const pc = pod.startsWith("FW")?"#b03030":pod.startsWith("SAC")?"#1a5fa0":pod==="F4"?"#5040b0":"var(--text3)";
        return "<div style='margin-top:3px'><span style='font-size:9px;font-weight:700;color:"+pc+";margin-right:4px'>"+pod+"</span>"+a+" vs "+h+"</div>";
      }).join("");
      blurb = "<div style='margin-bottom:4px'>"+blurb+"</div>"+rows;
    }
    tbdLines.push(blurb);
  });
  if(tbdLines.length){
    tbdBanner.style.display="block";
    tbdBanner.innerHTML = tbdLines.join("<div style='margin-top:8px'></div>");
  } else {
    tbdBanner.style.display="none";
  }

  // Day summary
  const sumEl = document.getElementById("daySummary");
  const scheduledGames = allGames.filter(g=>toLocalMin(g.time)!==null);
  const tbdGames = allGames.filter(g=>toLocalMin(g.time)===null);

  function genderBreakdown(games) {
    const w = games.filter(g=>g.gender==='W').length;
    const m = games.filter(g=>g.gender==='M').length;
    const parts = [];
    if(w) parts.push(w+" WBB");
    if(m) parts.push(m+" MBB");
    return parts.join(" + ");
  }

  if(!scheduledGames.length){
    // All TBD
    sumEl.textContent = genderBreakdown(allGames) + " games — times TBD";
  } else {
    const wbbG = scheduledGames.filter(g=>g.gender==='W');
    const mbbG = scheduledGames.filter(g=>g.gender==='M');
    let parts = [];
    if(wbbG.length) parts.push(wbbG.length+" WBB");
    if(mbbG.length) parts.push(mbbG.length+" MBB");
    const totals = parts.join(" + ");
    const allMins = scheduledGames.map(g=>toLocalMin(g.time));
    const first = Math.min(...allMins);
    const lastEnd = Math.max(...allMins)+120;
    function minToStr(m){let h=Math.floor(m/60)%24,mm=m%60,ap=h>=12?'PM':'AM';if(h>12)h-=12;if(h===0)h=12;return h+(mm>0?':'+String(mm).padStart(2,'0'):'')+' '+ap;}
    const _tzAbbr = _isUS?_tzInfo.abbr:'ET';
    const endStr = (lastEnd%1440===0||lastEnd>=1440)?'midnight':minToStr(lastEnd)+' '+_tzAbbr;
    let summary = totals + " games · "+minToStr(first)+" – "+endStr;
    if(tbdGames.length) summary += " · +" + genderBreakdown(tbdGames) + " times TBD";
    sumEl.textContent = summary;
  }

  // Determine which nets have games
  const visibleNets = (activeFilter==='wbb') ? WBB_NETS : (activeFilter==='mbb') ? MBB_NETS : ALL_NETS;
  const netsUsed = visibleNets.filter(n=>allGames.some(g=>g.net===n));

  if(!netsUsed.length){
    container.innerHTML="<div class='future-note'>No games found for this day/filter.</div>";
    return;
  }

  const realGames = allGames.filter(g=>toLocalMin(g.time)!==null);
  if(!realGames.length){
    container.innerHTML="<div class='future-note'>Game times not yet announced — check back soon.</div>";
    return;
  }

  // Max simultaneous games: sweep every minute, find peak overlap
  let maxSimul = 0;
  const schedMins = realGames.map(g => toLocalMin(g.time)).filter(Boolean);
  if(schedMins.length) {
    const sweepStart = Math.min(...schedMins);
    const sweepEnd   = Math.max(...schedMins) + DURATION;
    for(let t = sweepStart; t <= sweepEnd; t++) {
      const live = realGames.filter(g => {
        const s = toLocalMin(g.time);
        return s && t >= s && t < s + DURATION;
      }).length;
      if(live > maxSimul) maxSimul = live;
    }
  }
  note.style.display = maxSimul >= 2 ? "block" : "none";
  if(maxSimul >= 2) note.textContent = "You'd need " + maxSimul + " screens to catch every game live at peak overlap today!";

  const mins = realGames.map(g=>toLocalMin(g.time)).filter(Boolean);
  const dayStart = Math.floor((Math.min(...mins)-15)/30)*30;
  const dayEnd   = Math.ceil((Math.max(...mins)+DURATION+15)/30)*30;
  const totalMin = dayEnd-dayStart;
  const totalPx  = totalMin*PX_PER_MIN;

  const ticks=[];for(let t=dayStart;t<=dayEnd;t+=30)ticks.push(t);
  const nowN=new Date();
  const todStr=nowN.toLocaleDateString("en-US",{weekday:"short",month:"short",day:"numeric"}).replace(",","");
  const isToday=activeDay===todStr;
  const nowMin=nowN.getHours()*60+nowN.getMinutes();
  const showNow=isToday&&nowMin>=dayStart&&nowMin<=dayEnd;
  const nowPct=showNow?((nowMin-dayStart)/totalMin*100):null;

  let html="<div class='grid-wrap'>";
  html+="<div class='grid-header'>";
  html+="<div class='corner' style='width:"+TIME_COL_W+"px;min-width:"+TIME_COL_W+"px'>"+_tzLabel+"</div>";
  netsUsed.forEach(n=>{
    const cls = WBB_NETS.includes(n)?'wbb-ch':MBB_NETS.includes(n)?'mbb-ch':'';
    html+="<div class='ch-head "+cls+"'>"+n+"</div>";
  });
  html+="</div>";

  html+="<div class='grid-body'>";
  // Time column
  html+="<div class='time-col' style='width:"+TIME_COL_W+"px;min-width:"+TIME_COL_W+"px;height:"+totalPx+"px;position:relative'>";
  ticks.forEach(t=>{
    const yPct=(t-dayStart)/totalMin*100;
    const h24=Math.floor(t/60),m=t%60,ap=h24>=12?"PM":"AM",h12=h24>12?h24-12:(h24===0?12:h24);
    const lbl=m===0?(h12+" "+ap):(h12+":"+String(m).padStart(2,"0"));
    html+="<div class='time-label' style='top:"+yPct+"%'>"+lbl+"</div>";
    html+="<div style='position:absolute;right:0;left:0;top:"+yPct+"%;height:1px;background:var(--border)'></div>";
  });
  if(nowPct!==null)html+="<div style='position:absolute;right:0;left:0;top:"+nowPct+"%;height:2px;background:var(--red);opacity:0.8'></div>";
  html+="</div>";

  // Game columns
  html+="<div style='display:flex;flex:1;height:"+totalPx+"px;position:relative'>";
  ticks.forEach(t=>{
    const yPct=(t-dayStart)/totalMin*100;
    html+="<div style='position:absolute;left:0;right:0;top:"+yPct+"%;height:1px;background:var(--border);opacity:"+(t%60===0?0.5:0.2)+";z-index:0'></div>";
  });
  if(nowPct!==null)html+="<div class='now-line' style='top:"+nowPct+"%'><span class='now-label'>NOW</span></div>";

  // WBB/MBB section divider line
  if(activeFilter==='both'){
    const wbbCount = netsUsed.filter(n=>WBB_NETS.includes(n)).length;
    if(wbbCount>0 && wbbCount<netsUsed.length){
      const divPct = wbbCount/netsUsed.length*100;
      html+="<div style='position:absolute;top:0;bottom:0;left:"+divPct+"%;width:2px;background:var(--border2);z-index:6;opacity:0.6'></div>";
    }
  }

  const wandSVG="<svg width='10' height='10' viewBox='0 0 10 10' style='margin-left:2px;flex-shrink:0'><line x1='5' y1='0' x2='5' y2='3' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='5' y1='7' x2='5' y2='10' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='0' y1='5' x2='3' y2='5' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='7' y1='5' x2='10' y2='5' stroke='#7c3aed' stroke-width='1.2' stroke-linecap='round'/><line x1='1.5' y1='1.5' x2='3.5' y2='3.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><line x1='6.5' y1='6.5' x2='8.5' y2='8.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><line x1='8.5' y1='1.5' x2='6.5' y2='3.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><line x1='1.5' y1='8.5' x2='3.5' y2='6.5' stroke='#7c3aed' stroke-width='1' stroke-linecap='round'/><circle cx='5' cy='5' r='1.5' fill='#7c3aed'/></svg>";
  const bubbleSVG="<svg width='20' height='18' viewBox='0 0 20 18' style='margin-left:3px;flex-shrink:0;vertical-align:middle'><circle cx='7.5' cy='10' r='6' fill='rgba(56,189,248,0.15)' stroke='rgba(56,189,248,0.7)' stroke-width='1.1'/><circle cx='5.5' cy='8' r='1.8' fill='white' opacity='0.55'/><circle cx='8.5' cy='7' r='0.7' fill='white' opacity='0.45'/><circle cx='14.5' cy='7.5' r='3.5' fill='rgba(56,189,248,0.12)' stroke='rgba(56,189,248,0.6)' stroke-width='0.9'/><circle cx='13.2' cy='6' r='1' fill='white' opacity='0.55'/><circle cx='15' cy='13.5' r='2.2' fill='rgba(56,189,248,0.1)' stroke='rgba(56,189,248,0.55)' stroke-width='0.8'/><circle cx='14' cy='12.5' r='0.6' fill='white' opacity='0.5'/></svg>";

  netsUsed.forEach((net,ni)=>{
    const netGames=realGames.filter(g=>g.net===net);
    const leftPct=ni/netsUsed.length*100;
    const widthPct=1/netsUsed.length*100;
    html+="<div style='position:absolute;left:"+leftPct+"%;width:"+widthPct+"%;top:0;bottom:0;"+(ni<netsUsed.length-1?"border-right:1px solid var(--border)":"")+"'>";

    netGames.forEach(g=>{
      const s=toLocalMin(g.time);if(!s)return;
      const isWBB = g.gender==='W';
      const isMBB = g.gender==='M';
      const urlBase = isWBB
        ? (g.gameId?"https://www.espn.com/womens-college-basketball/game/_/gameId/"+g.gameId:"")
        : (g.gameId?"https://www.espn.com/mens-college-basketball/game/_/gameId/"+g.gameId:"https://www.cbssports.com/college-basketball/");
      const yPct=(s-dayStart)/totalMin*100;
      const hPct=DURATION/totalMin*100;
      const isFinal=g.status==="final";
      const awayWon=isFinal&&g.ascore!=null&&g.ascore>g.hscore;
      const homeWon=isFinal&&g.hscore!=null&&g.hscore>g.ascore;
      const awayCls=isFinal?(awayWon?"winner":"loser"):"";
      const homeCls=isFinal?(homeWon?"winner":"loser"):"";
      const awayLogoHtml=g.awayLogo?"<img src='"+g.awayLogo+"' class='team-logo'>":"";
      const homeLogoHtml=g.homeLogo?"<img src='"+g.homeLogo+"' class='team-logo'>":"";
      const awaySeeds=g.away.match(/^[(]([0-9]+)[)]/);
      const homeSeeds=g.home.match(/^[(]([0-9]+)[)]/);
      const awaySeed=awaySeeds?parseInt(awaySeeds[1]):null;
      const homeSeed=homeSeeds?parseInt(homeSeeds[1]):null;
      const isUpset=isFinal&&awaySeed&&homeSeed&&((awayWon&&awaySeed>homeSeed)||(homeWon&&homeSeed>awaySeed));
      const barCls=(isWBB?"game-bar wbb-bar":"game-bar mbb-bar")+(isUpset?" upset":"");
      const genderLbl=isWBB?"WBB":"MBB";
      const genderCls=isWBB?"wbb":"mbb";
      const awayWand=cinderellaTeams.has(g.away.replace(/^[(][0-9]+[)] */,"")+"|"+g.gender)?wandSVG:"";
      const homeWand=cinderellaTeams.has(g.home.replace(/^[(][0-9]+[)] */,"")+"|"+g.gender)?wandSVG:"";
      const awayBubble=isBubbleForDay(g.away,g.gender,g.day)?bubbleSVG:"";
      const homeBubble=isBubbleForDay(g.home,g.gender,g.day)?bubbleSVG:"";
      const isMobile = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
      function fmtMobile(s){
        const m=s.match(/^[(]([0-9]+)[)] *(.+)$/);
        return m ? m[2]+' ('+m[1]+')' : s;
      }
      const awayName=isMobile?fmtMobile(g.awayAbbr||g.awayShort||g.away):g.away;
      const homeName=isMobile?fmtMobile(g.homeAbbr||g.homeShort||g.home):g.home;

      if(urlBase)html+="<a href='"+urlBase+"' target='_blank' style='text-decoration:none;color:inherit;display:contents'>";
      html+="<div class='"+barCls+"' style='top:"+yPct+"%;height:"+hPct+"%'>";
      html+="<div style='position:absolute;top:3px;right:4px;font-size:7px;color:var(--text3);opacity:0.7;pointer-events:none'>open ↗</div>";
      const roundLbl=getRoundLabel(g.day,g.gender);
      html+="<div class='bar-gender "+genderCls+"'>"+genderLbl+(roundLbl?" · "+roundLbl:"")+"</div>";
      const cinLabel=(cinderellaTeams.has(g.away.replace(/^[(][0-9]+[)] */,"")+"|"+g.gender)||cinderellaTeams.has(g.home.replace(/^[(][0-9]+[)] */,"")+"|"+g.gender))?"<span style='font-size:7px;font-weight:800;color:#7c3aed;margin-left:5px;letter-spacing:.04em'>CINDERELLA</span>":"";
      if(g.reg&&g.reg!=="FF"&&g.reg!=="F4"&&g.reg!=="CHAMP"&&g.reg!=="S"&&g.reg!=="E"&&g.reg!=="W"&&g.reg!=="MW"){
        html+="<div class='bar-pod r-"+g.reg+"' style='display:flex;align-items:center'>"+g.reg+cinLabel+"</div>";
      } else if(g.reg) {
        html+="<div class='bar-pod' style='color:var(--text3);display:flex;align-items:center'>"+g.reg+cinLabel+"</div>";
      } else if(cinLabel) {
        html+="<div class='bar-pod' style='display:flex;align-items:center'>"+cinLabel+"</div>";
      }
      html+="<div class='bar-team "+awayCls+"'>"+awayLogoHtml+awayName+awayWand+awayBubble+"</div>";
      html+="<div class='bar-team "+homeCls+"'>"+homeLogoHtml+homeName+homeWand+homeBubble+"</div>";
      if(isFinal&&g.ascore!=null)html+="<div class='bar-score-line'>"+g.ascore+" – "+g.hscore+"</div>";
      if(isUpset)html+="<div class='upset-label'>UNDERDOG UPSET</div>";
      if(g.time&&g.time!=='TBD'&&g.time!=='12:00 AM'){
        const lt=toLocalTime(g.time);
        if(lt){const _tDisp=lt.replace(':00','');html+="<div style='font-size:7px;color:var(--text3);margin-top:1px'>"+_tDisp+" "+(_isUS?_tzInfo.abbr:'ET')+" start</div>";}
      }
      if(g.venue&&g.venue!=="TBD"){
        const vparts=g.venue.split(', ');
        const vCity=vparts.slice(1).join(', ');
        html+="<div class='bar-venue'>"+(vCity||g.venue)+"</div>";
      }
      if(urlBase)html+="<div class='bar-link'>Open page &#8599;</div>";
      html+="</div>";
      if(urlBase)html+="</a>";
    });
    html+="</div>";
  });
  html+="</div></div></div>";
  container.innerHTML=html;
}

// ─────────────────────────────────────────────
// NAV
// ─────────────────────────────────────────────
function navStep(dir){
  const idx=days.indexOf(activeDay),ni=idx+dir;
  if(ni<0||ni>=days.length)return;
  activeDay=days[ni];
  document.querySelectorAll(".day-btn").forEach((b,i)=>{
    b.classList.remove("active");
    if(days[i]===activeDay){b.classList.add("active");b.scrollIntoView({behavior:"smooth",block:"nearest",inline:"center"});}
  });
  updateNavArrows();render();
}
function updateNavArrows(){
  const idx=days.indexOf(activeDay);
  const l=document.getElementById("navLeft"),r=document.getElementById("navRight");
  if(l)l.style.display=idx===0?"none":"flex";
  if(r)r.style.display=idx===days.length-1?"none":"flex";
}

// ─────────────────────────────────────────────
// SWIPE
// ─────────────────────────────────────────────
let _tx=0,_ty=0;
document.addEventListener('touchstart',e=>{_tx=e.touches[0].clientX;_ty=e.touches[0].clientY;},{passive:true});
document.addEventListener('touchend',e=>{
  const dx=e.changedTouches[0].clientX-_tx,dy=e.changedTouches[0].clientY-_ty;
  if(Math.abs(dx)<50||Math.abs(dx)<Math.abs(dy)*1.5)return;
  navStep(dx<0?1:-1);
},{passive:true});

// ─────────────────────────────────────────────
// STICKY HEIGHT
// ─────────────────────────────────────────────
function updateStickyHeight(){
  const ph=document.querySelector('body>div[style*="sticky"]');
  const phH = ph ? ph.offsetHeight : 0;
  if(ph) document.documentElement.style.setProperty('--header-h', phH+'px');
  const sd=document.getElementById('stickyDay');
  const sdH = sd ? sd.offsetHeight : 0;
  // grid-header must sit below persistent header + sticky day bar combined
  document.documentElement.style.setProperty('--sticky-h', (phH + sdH)+'px');
}
updateStickyHeight();
window.addEventListener('resize',updateStickyHeight);

// ─────────────────────────────────────────────
// VISIBILITY RELOAD
// ─────────────────────────────────────────────
let _ha=null;
document.addEventListener('visibilitychange',()=>{
  if(document.hidden){_ha=Date.now();}
  else{if(_ha&&Date.now()-_ha>15*60*1000){location.reload();}_ha=null;}
});

// ─────────────────────────────────────────────
// INIT
// ─────────────────────────────────────────────
buildTabs();render();updateStickyHeight();updateNavArrows();
</script>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────
# DATE LISTS
# ─────────────────────────────────────────────────────────────

WBB_DATES = [
    "20260318", "20260319",           # First Four
    "20260320", "20260321",           # Round 1
    "20260322", "20260323",           # Round 2
    "20260327", "20260328",           # Sweet 16
    "20260329", "20260330",           # Elite Eight
    "20260403",                       # Final Four
    "20260405",                       # Championship
]

MBB_DATES = [
    "20260317", "20260318",           # First Four
    "20260319", "20260320",           # Round 1
    "20260321", "20260322",           # Round 2
    "20260326", "20260327",           # Sweet 16
    "20260328", "20260329",           # Elite Eight
    "20260404",                       # Final Four
    "20260406",                       # Championship
]

DATE_DISPLAY = {
    "20260317": "Tue Mar 17",
    "20260318": "Wed Mar 18",
    "20260319": "Thu Mar 19",
    "20260320": "Fri Mar 20",
    "20260321": "Sat Mar 21",
    "20260322": "Sun Mar 22",
    "20260323": "Mon Mar 23",
    "20260326": "Thu Mar 26",
    "20260327": "Fri Mar 27",
    "20260328": "Sat Mar 28",
    "20260329": "Sun Mar 29",
    "20260330": "Mon Mar 30",
    "20260403": "Fri Apr 3",
    "20260404": "Sat Apr 4",
    "20260405": "Sun Apr 5",
    "20260406": "Mon Apr 6",
}

# ─────────────────────────────────────────────────────────────
# WBB REGION DETECTION
# The WBB tournament uses named pods (Fort Worth, Sacramento).
# We read the headline notes from the ESPN event to identify them.
# ─────────────────────────────────────────────────────────────

WBB_REGION_MAP = {
    "regional 1 in fort worth": "FW1",
    "regional 2 in sacramento": "SAC2",
    "regional 3 in fort worth": "FW3",
    "regional 4 in sacramento": "SAC4",
    "final four":               "F4",
    "national championship":    "F4",
}

# MBB uses standard bracket regions.
# ESPN puts the region name in the notes headline e.g. "East Regional".
MBB_REGION_MAP = {
    "east":     "E",
    "west":     "W",
    "south":    "S",
    "midwest":  "MW",
    "first four": "FF",
    "final four": "F4",
    "national championship": "CHAMP",
}

# ─────────────────────────────────────────────────────────────
# ESPN API FETCH
# ─────────────────────────────────────────────────────────────

WBB_API = "https://site.api.espn.com/apis/site/v2/sports/basketball/womens-college-basketball/scoreboard?dates={date}"
MBB_API = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates={date}"

def fetch_events(url_template, date_str):
    url = url_template.format(date=date_str)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            return data.get("events", [])
    except Exception as e:
        print(f"    Error fetching {date_str}: {e}")
        return []

def is_tournament_game(event):
    """Filter to NCAA Tournament games only (not NIT etc.)"""
    try:
        abbr = event["competitions"][0].get("type", {}).get("abbreviation", "")
        return abbr == "TRNMNT"
    except:
        return False

# ─────────────────────────────────────────────────────────────
# FIELD EXTRACTORS  (shared by WBB and MBB)
# ─────────────────────────────────────────────────────────────

def get_teams(event):
    try:
        competitors = event["competitions"][0]["competitors"]
        home = next(c for c in competitors if c["homeAway"] == "home")
        away = next(c for c in competitors if c["homeAway"] == "away")
        return (
            away["team"]["displayName"],
            home["team"]["displayName"],
            away.get("curatedRank", {}).get("current", ""),
            home.get("curatedRank", {}).get("current", ""),
            away["team"].get("logo", ""),
            home["team"].get("logo", ""),
            away["team"].get("shortDisplayName", away["team"]["displayName"]),
            home["team"].get("shortDisplayName", home["team"]["displayName"]),
            away["team"].get("abbreviation", ""),
            home["team"].get("abbreviation", ""),
        )
    except:
        return "TBD", "TBD", "", "", "", "", "TBD", "TBD", "", ""

def get_time(event):
    try:
        detail = event["status"]["type"]["detail"]
        match = re.search(r'at\s+([\d:]+\s*[AP]M)', detail)
        if match:
            return match.group(1).strip()
        date_str = event.get("date", "")
        if date_str:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%MZ")
            dt_et = dt - timedelta(hours=4)   # UTC → ET (rough — good enough for display)
            h, m = dt_et.hour, dt_et.minute
            ap = "PM" if h >= 12 else "AM"
            h12 = h - 12 if h > 12 else (12 if h == 0 else h)
            return f"{h12}:{str(m).zfill(2)} {ap}"
    except:
        pass
    return "TBD"

def get_network(event):
    try:
        broadcasts = event["competitions"][0].get("broadcasts", [])
        if broadcasts:
            names = broadcasts[0].get("names", [])
            if names:
                return names[0]
    except:
        pass
    return ""

def get_venue(event):
    try:
        venue = event["competitions"][0]["venue"]
        city  = venue["address"]["city"]
        state = venue["address"]["state"]
        name  = venue.get("fullName", "")
        return f"{name}, {city}, {state}" if name else f"{city}, {state}"
    except:
        return "TBD"

def get_status(event):
    try:
        status_obj = event["competitions"][0].get("status", event.get("status", {}))
        completed  = status_obj["type"]["completed"]
        state      = status_obj["type"]["state"]
        if completed:
            return "final"
        if state == "in":
            return "live"
    except:
        pass
    return "upcoming"

def get_scores(event):
    try:
        competitors = event["competitions"][0]["competitors"]
        home  = next(c for c in competitors if c["homeAway"] == "home")
        away  = next(c for c in competitors if c["homeAway"] == "away")
        ascore = int(float(away.get("score", 0)))
        hscore = int(float(home.get("score", 0)))
        if ascore == 0 and hscore == 0:
            return None, None
        return ascore, hscore
    except:
        return None, None

def get_game_id(event):
    try:
        return str(event.get("id", ""))
    except:
        return ""

def format_team(name, seed):
    if seed and str(seed) not in ("", "99"):
        return f"({seed}) {name}"
    return name

# ─────────────────────────────────────────────────────────────
# REGION DETECTION
# ─────────────────────────────────────────────────────────────

def detect_region(event, region_map):
    try:
        notes = event["competitions"][0].get("notes", [])
        for note in notes:
            headline = note.get("headline", "").lower()
            for key, reg in region_map.items():
                if key in headline:
                    return reg
        # Also check competition notes at event level
        for note in event.get("notes", []):
            headline = note.get("headline", "").lower()
            for key, reg in region_map.items():
                if key in headline:
                    return reg
    except:
        pass
    return None

# ─────────────────────────────────────────────────────────────
# ENTRY BUILDER
# Produces one JS object string for the G_WBB or G_MBB array.
# ─────────────────────────────────────────────────────────────

def build_entry(day, time, net, away, home, reg, venue, status,
                ascore, hscore, away_logo, home_logo,
                away_short="", home_short="",
                away_abbr="", home_abbr="", game_id=""):

    def esc(s):
        return str(s).replace('"', '\\"')

    entry = (
        f'  {{day:"{esc(day)}",time:"{esc(time)}",net:"{esc(net)}",'
        f'away:"{esc(away)}",home:"{esc(home)}",'
        f'awayShort:"{esc(away_short)}",homeShort:"{esc(home_short)}",'
        f'awayAbbr:"{esc(away_abbr)}",homeAbbr:"{esc(home_abbr)}",'
        f'gameId:"{esc(game_id)}",reg:"{esc(reg)}",'
        f'venue:"{esc(venue)}",'
        f'awayLogo:"{esc(away_logo)}",homeLogo:"{esc(home_logo)}"'
    )
    if status == "final" and ascore is not None and hscore is not None:
        entry += f',ascore:{ascore},hscore:{hscore},status:"final"'
    elif status == "live":
        entry += ',status:"live"'
    entry += '},'
    return entry

# ─────────────────────────────────────────────────────────────
# FETCH ALL WBB GAMES
# ─────────────────────────────────────────────────────────────

def fetch_wbb_games():
    print("  Fetching WBB games from ESPN...")
    all_entries = []
    all_events_by_date = {}

    for date_str in WBB_DATES:
        events = fetch_events(WBB_API, date_str)
        tourney = [e for e in events if is_tournament_game(e)]
        all_events_by_date[date_str] = tourney

    # Build pod lookup from known-region games (helps fill TBD pods in later rounds)
    team_to_pod = {}
    for date_str, events in all_events_by_date.items():
        for event in events:
            reg = detect_region(event, WBB_REGION_MAP)
            if reg and reg != "F4":
                away_full, home_full = get_teams(event)[:2]
                if away_full != "TBD":
                    team_to_pod[away_full] = reg
                if home_full != "TBD":
                    team_to_pod[home_full] = reg

    total = 0
    for date_str in WBB_DATES:
        day_label = DATE_DISPLAY[date_str]
        events    = all_events_by_date.get(date_str, [])
        if not events:
            continue
        print(f"    {day_label}: {len(events)} WBB game(s)")
        total += len(events)

        for event in events:
            (away_full, home_full, away_seed, home_seed,
             away_logo, home_logo,
             away_short_name, home_short_name,
             away_abbr_raw, home_abbr_raw) = get_teams(event)

            away   = format_team(away_full, away_seed)
            home   = format_team(home_full, home_seed)
            time   = get_time(event)
            net    = get_network(event)
            venue  = get_venue(event)
            status = get_status(event)
            ascore, hscore = get_scores(event) if status == "final" else (None, None)

            reg = detect_region(event, WBB_REGION_MAP)
            if reg is None:
                reg = team_to_pod.get(away_full) or team_to_pod.get(home_full) or "F4"

            entry = build_entry(
                day_label, time, net,
                away, home, reg, venue, status, ascore, hscore,
                away_logo, home_logo,
                format_team(away_short_name, away_seed),
                format_team(home_short_name, home_seed),
                format_team(away_abbr_raw, away_seed),
                format_team(home_abbr_raw, home_seed),
                get_game_id(event),
            )
            all_entries.append(entry)

    print(f"    Total WBB: {total} games")
    return all_entries

# ─────────────────────────────────────────────────────────────
# FETCH ALL MBB GAMES
# ─────────────────────────────────────────────────────────────

def fetch_mbb_games():
    print("  Fetching MBB games from ESPN...")
    all_entries = []
    total = 0

    for date_str in MBB_DATES:
        day_label = DATE_DISPLAY[date_str]
        events    = fetch_events(MBB_API, date_str)
        tourney   = [e for e in events if is_tournament_game(e)]
        if not tourney:
            continue
        print(f"    {day_label}: {len(tourney)} MBB game(s)")
        total += len(tourney)

        for event in tourney:
            (away_full, home_full, away_seed, home_seed,
             away_logo, home_logo,
             away_short_name, home_short_name,
             away_abbr_raw, home_abbr_raw) = get_teams(event)

            away   = format_team(away_full, away_seed)
            home   = format_team(home_full, home_seed)
            time   = get_time(event)
            net    = get_network(event)
            venue  = get_venue(event)
            status = get_status(event)
            ascore, hscore = get_scores(event) if status == "final" else (None, None)

            reg = detect_region(event, MBB_REGION_MAP) or "E"

            entry = build_entry(
                day_label, time, net,
                away, home, reg, venue, status, ascore, hscore,
                away_logo, home_logo,
                format_team(away_short_name, away_seed),
                format_team(home_short_name, home_seed),
                format_team(away_abbr_raw, away_seed),
                format_team(home_abbr_raw, home_seed),
                get_game_id(event),
            )
            all_entries.append(entry)

    print(f"    Total MBB: {total} games")
    return all_entries

# ─────────────────────────────────────────────────────────────
# BACKUP
# ─────────────────────────────────────────────────────────────

def backup_html():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(BACKUP_DIR, f"combined_schedule_{ts}.html")
    shutil.copy2(HTML_FILE, path)
    print(f"  Backup saved: {path}")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*60)
    print("  Combined MBB + WBB Schedule Updater")
    print(f"  {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    print("="*60)

    # ── 1. Backup existing output if it exists ─────────────────
    print("\n[1] Backing up current file...")
    if os.path.exists(HTML_FILE):
        backup_html()
    else:
        print("  No existing file to back up — fresh build.")

    # ── 2. Fetch games ─────────────────────────────────────────
    print("\n[2] Fetching games from ESPN API...")
    wbb_entries = fetch_wbb_games()
    mbb_entries = fetch_mbb_games()

    if not wbb_entries:
        print("\n  WARNING: No WBB games returned — WBB data will be empty.")
    if not mbb_entries:
        print("\n  WARNING: No MBB games returned — MBB data will be empty.")

    # ── 3. Build HTML from embedded template ───────────────────
    print("\n[3] Building fresh HTML from template...")
    wbb_block = "\n".join(wbb_entries)
    mbb_block = "\n".join(mbb_entries)

    html = HTML_TEMPLATE.replace("%%WBB_DATA%%", wbb_block)
    html = html.replace("%%MBB_DATA%%", mbb_block)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print("  Done.")

    # ── 4. Verify ──────────────────────────────────────────────
    print("\n[4] Verifying output...")
    with open(HTML_FILE, encoding="utf-8") as f:
        content = f.read()

    import collections
    wbb_games  = len(re.findall(r'day:".*?".*?net:"(?:ESPN|ABC|ESPN2|ESPNU|ESPNews)', content))
    mbb_games  = len(re.findall(r'day:".*?".*?net:"(?:CBS|TBS|TNT|truTV)', content))
    finals     = len(re.findall(r'status:"final"', content))
    live       = len(re.findall(r'status:"live"', content))

    print(f"  WBB games : {wbb_games}")
    print(f"  MBB games : {mbb_games}")
    print(f"  Finals    : {finals}")
    print(f"  Live      : {live}")
    print(f"\n  --> {HTML_FILE} is ready.")
    print("\n" + "="*60)
    print("  Finished!")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
