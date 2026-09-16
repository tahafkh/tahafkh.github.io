---
layout: page
permalink: /bands/
title: bands
description: Bands I keep coming back to.
nav: true
nav_order: 5
---

<style>
  .likes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
  }
  .likes-card {
    display: block;
    padding: 1rem 1.1rem;
    border: 1px solid color-mix(in srgb, currentColor 18%, transparent);
    border-radius: 8px;
    background: color-mix(in srgb, currentColor 4%, transparent);
    color: inherit;
    text-decoration: none;
    transition: border-color 0.15s ease, transform 0.15s ease;
  }
  a.likes-card:hover {
    border-color: color-mix(in srgb, currentColor 40%, transparent);
    transform: translateY(-2px);
    text-decoration: none;
  }
  .likes-name {
    font-weight: 600;
    font-size: 1.05rem;
    line-height: 1.3;
  }
  .likes-meta {
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-top: 0.2rem;
  }
  .likes-note {
    font-size: 0.9rem;
    opacity: 0.85;
    margin-top: 0.55rem;
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
    .likes-card { transition: none; }
    a.likes-card:hover { transform: none; }
  }
</style>

Music is what's on while I'm reading, writing, or failing to debug something. This is the short list — the ones that survived the move to Okinawa.

{% assign bands = site.data.bands.bands %}
{% if bands and bands.size > 0 %}

<div class="likes-grid">
{% for band in bands %}
  {% if band.url %}<a class="likes-card" href="{{ band.url }}">{% else %}<div class="likes-card">{% endif %}
    <div class="likes-name">{{ band.name }}</div>
    {% if band.genre or band.since %}
      <div class="likes-meta">
        {{ band.genre }}{% if band.genre and band.since %} · {% endif %}{% if band.since %}since {{ band.since }}{% endif %}
      </div>
    {% endif %}
    {% if band.note %}<div class="likes-note">{{ band.note }}</div>{% endif %}
  {% if band.url %}</a>{% else %}</div>{% endif %}
{% endfor %}
</div>

{% else %}

<div class="likes-empty">
  Still putting this list together — check back shortly.
</div>

{% endif %}
