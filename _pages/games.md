---
layout: page
permalink: /games/
title: games
description: Games worth the hours.
nav: true
nav_order: 6
---

<style>
  .games-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 1.2rem;
    margin-top: 1.5rem;
  }
  .game-card {
    display: block;
    border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
    border-radius: 8px;
    overflow: hidden;
    background: color-mix(in srgb, currentColor 4%, transparent);
    color: inherit;
    text-decoration: none;
    transition: border-color 0.15s ease, transform 0.15s ease;
  }
  a.game-card:hover {
    border-color: color-mix(in srgb, currentColor 40%, transparent);
    transform: translateY(-2px);
    text-decoration: none;
  }
  .game-cover {
    display: block;
    width: 100%;
    aspect-ratio: 92 / 43;
    object-fit: cover;
    max-width: 100%;
    background: color-mix(in srgb, currentColor 10%, transparent);
  }
  .game-body { padding: 0.85rem 1rem 1rem; }
  .game-name { font-weight: 600; font-size: 1.02rem; line-height: 1.3; }
  .game-meta {
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-top: 0.2rem;
  }
  .game-note {
    font-size: 0.9rem;
    opacity: 0.85;
    margin-top: 0.5rem;
    line-height: 1.45;
  }
  .likes-empty {
    margin-top: 1.5rem;
    padding: 1.4rem;
    border: 1px dashed color-mix(in srgb, currentColor 30%, transparent);
    border-radius: 8px;
    opacity: 0.75;
  }
  @media (prefers-reduced-motion: reduce) {
    .game-card { transition: none; }
    a.game-card:hover { transform: none; }
  }
</style>

Not a completionist list — just the ones I'd reinstall. Cover art for anything on Steam is pulled straight from their CDN, so there are no image files to keep around.

{% assign games = site.data.games.games %}
{% if games and games.size > 0 %}

<div class="games-grid">
{% for game in games %}
  {% if game.url %}<a class="game-card" href="{{ game.url }}">{% else %}<div class="game-card">{% endif %}
    {% if game.steam_appid %}
      <img
        class="game-cover"
        loading="lazy"
        src="https://cdn.cloudflare.steamstatic.com/steam/apps/{{ game.steam_appid }}/header.jpg"
        alt="{{ game.name }} cover art"
      />
    {% elsif game.cover %}
      <img class="game-cover" loading="lazy" src="{{ game.cover | relative_url }}" alt="{{ game.name }} cover art" />
    {% endif %}
    <div class="game-body">
      <div class="game-name">{{ game.name }}</div>
      {% if game.platform or game.year %}
        <div class="game-meta">
          {{ game.platform }}{% if game.platform and game.year %} · {% endif %}{{ game.year }}
        </div>
      {% endif %}
      {% if game.note %}<div class="game-note">{{ game.note }}</div>{% endif %}
    </div>
  {% if game.url %}</a>{% else %}</div>{% endif %}
{% endfor %}
</div>

{% else %}

<div class="likes-empty">
  Still putting this list together — check back shortly.
</div>

{% endif %}
