# tahafkh.github.io

Personal academic website of **Mohammad Taha Fakharian** — Ph.D. student at [OIST](https://www.oist.jp/), Machine Learning and Data Science Unit.

Live at **<https://tahafkh.github.io>**.

Built on the [al-folio](https://github.com/alshedivat/al-folio) v1.x starter, which is a thin Jekyll wrapper around versioned `al-*` gems. The upstream docs live in [`docs/`](docs/) and still apply.

## Where things live

| What you want to change              | File                                                            |
| ------------------------------------ | --------------------------------------------------------------- |
| Bio, photo, homepage text            | `_pages/about.md`, `assets/img/prof_pic.jpg`                    |
| Papers                               | `_bibliography/papers.bib`                                      |
| News items on the homepage           | `_news/*.md` (one file each, `inline: true` for one-liners)     |
| Notes / blog posts                   | `_posts/YYYY-MM-DD-slug.md`                                     |
| CV                                   | **Overleaf** (`cv.tex`) — never `_data/cv.yml`, it is generated |
| Bands page                           | `_data/bands.yml`                                               |
| Games page                           | `_data/games.yml`                                               |
| Repos shown on `/repositories/`      | `_data/repositories.yml`                                        |
| Social links and Scholar ID          | `_data/socials.yml`                                             |
| Site title, favicon, feature toggles | `_config.yml`                                                   |

## Two things that will silently break the site

1. **`baseurl` must stay blank.** This is a GitHub _user_ site served from the domain root. Setting `baseurl: /al-folio` (the upstream default) makes every stylesheet and link resolve to `tahafkh.github.io/al-folio/...`, which 404s — the page renders as unstyled HTML.
2. **`Gemfile` and `_config.yml` are two lists that must agree.** A plugin listed in only one of them is inert, with no warning and no error.
3. **`_data/cv.yml` is generated — never edit it.** It is rebuilt from the Overleaf LaTeX project by `bin/cv_from_latex.py`, so hand edits are silently overwritten on the next sync. Edit the CV on Overleaf. The only exceptions are `summary`, `image` and `address`, which have no LaTeX source and are carried across each regeneration.

## Keeping the CV in sync with Overleaf

The Awesome-CV project on Overleaf is the single source of truth. After editing it there, run:

```bash
bin/sync-cv          # pull ../cv from Overleaf, regenerate _data/cv.yml, show the diff
bin/sync-cv --no-pull        # skip the fetch, use the checkout already on disk
bin/sync-cv ~/elsewhere/cv   # point at a different path
```

then review and commit.

**This runs locally rather than in CI, deliberately.** An Overleaf Git token authenticates as _you_ and grants read and write to **every project on your account**, not just this one. This repository is public. GitHub Actions secrets are encrypted and are never handed to pull requests from forks, so storing it would probably be fine — but "probably fine" is the wrong standard for a credential with that blast radius, to save one command on a document that changes a few times a year. Running it locally reuses the Overleaf credentials your git client already has, and no token ever leaves your machine.

The parser is deliberately strict: an unrecognised macro shape stops the run with an error rather than silently writing a half-parsed CV.

## Automation

| Workflow               | Does what                                                                         |
| ---------------------- | --------------------------------------------------------------------------------- |
| `deploy.yml`           | Builds and publishes to the `gh-pages` branch on every push to `main`             |
| `update-citations.yml` | Refreshes Google Scholar citation counts into `_data/citations.yml` (Mon/Wed/Fri) |
| `prettier.yml`         | Formatting check — run `npx prettier . --write` before pushing                    |

## Local development

Needs Ruby 3.3+ and Bundler.

```bash
bundle install
bundle exec jekyll serve   # http://localhost:4000
```

Note: unlike the upstream template, **do not** pass `--baseurl /al-folio`.

## License

Site content © Mohammad Taha Fakharian. The al-folio starter is MIT licensed — see [`LICENSE`](LICENSE).
