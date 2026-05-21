---
name: publish-setup
description: Use after a repo has been bootstrapped from py-template (or any sibling template) and the user wants to wire up GitHub Pages docs deployment and/or PyPI publishing. Trigger keywords - "enable github pages", "publish docs", "configure mkdocs deploy", "pypi publish", "trusted publishing", "set up release", "finish template setup", "post-clone setup", "enable publishing", "configure pages and pypi", "first release", "ship to pypi", "启用 pages", "发布到 pypi", "配置文档站", "配置发布".
---

# publish-setup — wire up GitHub Pages + PyPI Trusted Publishing

This skill applies to repos generated from `rararulab/py-template` (or any
project that uses the same `mkdocs.yml` + `release-please.yml` layout).
It walks an agent or a human through the two **one-time, GitHub-side**
configuration steps that the template cannot perform itself.

Run the steps in order. Each has a verifiable success signal — paste the
signal into the response before claiming the step is done (per the
project's verification-before-completion discipline).

## Prerequisites — verify first

Before doing anything, confirm the repo state:

```bash
# 1. We are inside a clone of a py-template-derived repo.
test -f mkdocs.yml -a -f .release-please-config.json \
  -a -f .github/workflows/docs.yml -a -f .github/workflows/release-please.yml \
  && echo "ok: template files present" \
  || { echo "fail: this repo does not look like py-template output"; exit 1; }

# 2. Remote is GitHub and we know owner/repo.
gh repo view --json nameWithOwner -q .nameWithOwner

# 3. gh is authenticated with admin scope (needed to flip Pages + branch settings).
gh auth status
```

If `gh auth status` does not include `admin:repo` or the user is not a repo
admin, stop and ask the user to run `gh auth refresh -s admin:repo` (or to
perform the GitHub-UI steps themselves while you stand by).

---

## Part 1 — GitHub Pages (docs site)

**Goal:** every push to `main` that touches `docs/**`, `mkdocs.yml`, or
`src/**` deploys the mkdocs-material site to `https://<owner>.github.io/<repo>/`.

The template ships `.github/workflows/docs.yml` which runs
`mkdocs gh-deploy --force`. That action pushes the built site to a
`gh-pages` branch. The branch does not exist until the workflow has run
**once**, so Pages cannot be configured before the first deploy.

### Step 1.1 — Trigger the first docs build

Pick whichever applies:

- **If `main` already has commits:** push any change touching `docs/` or
  `mkdocs.yml`, **or** manually dispatch:
  ```bash
  gh workflow run docs.yml
  gh run watch  # wait until green
  ```
- **If the repo is empty:** make the initial commit + push to `main`
  first; `docs.yml` is gated on changes under `docs/**`, so a `docs:`
  commit will trigger it.

**Success signal:** `gh-pages` branch exists.

```bash
gh api repos/{owner}/{repo}/branches/gh-pages --jq .name
# → gh-pages
```

If the workflow failed, read the log (`gh run view --log-failed`) and
fix it before continuing. Common failure: `mkdocs.yml` references a
`docs/` page that does not exist — `mkdocs build -s` locally surfaces it.

### Step 1.2 — Point Pages at the `gh-pages` branch

Two paths. **Prefer the API call** — it is scriptable and idempotent.

```bash
OWNER=$(gh repo view --json owner -q .owner.login)
REPO=$(gh repo view --json name  -q .name)

gh api -X POST "repos/$OWNER/$REPO/pages" \
  -f source[branch]=gh-pages \
  -f source[path]=/ \
  || gh api -X PUT "repos/$OWNER/$REPO/pages" \
       -f source[branch]=gh-pages \
       -f source[path]=/
```

(The POST creates the Pages site; if it already exists, the PUT updates
the source. Run both — the second is a no-op on a fresh repo.)

Manual fallback if the user prefers the UI:

> Settings → Pages → **Build and deployment** → Source: **Deploy from a
> branch** → Branch: **gh-pages** / **/ (root)** → Save.

### Step 1.3 — Verify

```bash
# API reports the live URL.
gh api "repos/$OWNER/$REPO/pages" --jq '.html_url, .status'
# → https://<owner>.github.io/<repo>/
# → built

# Curl the page (allow ~30s for first deploy to propagate).
URL=$(gh api "repos/$OWNER/$REPO/pages" --jq .html_url)
curl -sfI "$URL" | head -1
# → HTTP/2 200
```

**Done signal to paste:** the live URL plus `HTTP/2 200`.

---

## Part 2 — PyPI Trusted Publishing (release wheels)

**Goal:** when release-please merges its release PR and the
`release-please.yml` workflow runs `pypa/gh-action-pypi-publish`, PyPI
accepts the upload via OIDC — **no API token stored in GitHub secrets**.

The template ships the publish step **commented out** at the bottom of
`.github/workflows/release-please.yml`. We register the trusted publisher
on PyPI first, then uncomment.

### Step 2.1 — Decide: PyPI or TestPyPI first?

Default recommendation: register on **TestPyPI** first, ship `0.0.1` there
to validate the pipeline, then register on PyPI for real. Skip TestPyPI
only if the user explicitly says so. Ask:

> "Want to dry-run the release on TestPyPI first, or go straight to PyPI?"

The setup is identical; only the host differs (`test.pypi.org` vs
`pypi.org`). Trusted Publishing must be configured on **each** host
separately.

### Step 2.2 — Register the trusted publisher on PyPI

This requires the **PyPI account owner's browser session**. The agent
cannot do it via `gh` — PyPI has no GitHub-side API for it.

Tell the user (paste this verbatim, filling in the placeholders):

> Open https://pypi.org/manage/account/publishing/ (or
> https://test.pypi.org/manage/account/publishing/ for TestPyPI).
> Under **Add a new pending publisher** fill in:
>
> - **PyPI Project Name:** `<distribution name from pyproject.toml>`
> - **Owner:** `<github-owner>`
> - **Repository name:** `<github-repo>`
> - **Workflow name:** `release-please.yml`
> - **Environment name:** *(leave blank unless you add one in Step 2.4)*
>
> Click **Add**. Tell me when done.

You can fetch the distribution name automatically:

```bash
python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['name'])"
```

A "pending publisher" is fine if the project does not exist on PyPI yet —
the first successful publish creates it and converts the pending entry
into a real one. For an existing PyPI project, the user adds the publisher
under **Your projects → \<project\> → Publishing**.

### Step 2.3 — Uncomment the publish step

Edit `.github/workflows/release-please.yml`. Find the commented block at
the end of the `build-and-publish` job and uncomment it:

```yaml
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          packages-dir: dist/
          skip-existing: true
```

For TestPyPI, also set `repository-url`:

```yaml
        with:
          packages-dir: dist/
          skip-existing: true
          repository-url: https://test.pypi.org/legacy/
```

The job already has `permissions: id-token: write` at the workflow level
— that is what enables OIDC. Do not remove it.

Commit with `ci: enable PyPI Trusted Publishing` and merge.

### Step 2.4 — Optional: gate publish behind a GitHub Environment

For production PyPI, recommend (don't force) creating a `pypi` environment
with required reviewers so a human approves each release upload.

```bash
# Create the environment (idempotent).
gh api -X PUT "repos/$OWNER/$REPO/environments/pypi" >/dev/null
echo "created environment: pypi"
```

Then in `release-please.yml`, add at the **job** level (not step):

```yaml
  build-and-publish:
    ...
    environment:
      name: pypi
      url: https://pypi.org/p/<project-name>
```

And on PyPI's publisher form (Step 2.2) fill in **Environment name: `pypi`**.

If you add the environment after registering the publisher without it,
**update the publisher entry on PyPI** to match — mismatched environment
names cause OIDC verification to fail with `invalid-publisher`.

### Step 2.5 — Verify

Trigger a real release through release-please (or manually dispatch a
test release). Watch the `Publish to PyPI` step:

```bash
gh run watch
```

**Success signals:**

- Step log contains `Uploading distributions to https://upload.pypi.org/legacy/`
  followed by `... done`.
- `pip install <project-name>==<new-version>` from a clean venv works.
- `https://pypi.org/project/<project-name>/<version>/` resolves with the
  release notes from `CHANGELOG.md`.

If the step fails with `invalid-publisher`:

1. Owner / repo / workflow name on PyPI must match **exactly** (case-sensitive).
2. Environment name on PyPI must match the workflow's `environment.name`
   (or both must be blank).
3. The workflow file must live at `.github/workflows/release-please.yml`
   on the **default branch** — PyPI checks the path, not just the name.

---

## Done checklist

After both parts, the repo has:

- [ ] `gh-pages` branch exists and Pages serves `https://<owner>.github.io/<repo>/`.
- [ ] `docs.yml` ran green at least once; the live site shows the home page.
- [ ] PyPI trusted publisher registered (or TestPyPI, per the user's choice).
- [ ] `release-please.yml` has the `Publish to PyPI` step uncommented and committed.
- [ ] (Recommended) `pypi` environment exists and is named on both sides.
- [ ] At least one tagged release has uploaded a wheel + sdist that
      `pip install` can fetch.

Paste each checked item's success signal (URL, HTTP status, PyPI link)
into the final report. Don't tick a box without the signal.
