# Deploy the docs

The docs site is built with VitePress, a Node documentation
package, from the Markdown already in this repo. No Markdown
file is moved for the site, and no frontmatter is added to
existing pages, so they stay readable on GitHub exactly as
before. VitePress only renders them, with a sidebar, search,
and clean URLs.

Why VitePress, and not a Python generator: Vercel already
failed this repo as a Python app, with "No python entrypoint
found", because it detected the Python library in `lib/python`
and tried to deploy it as a web app. A Node build, with an
explicit `npm run docs:build` command and a VitePress
framework in `vercel.json`, tells Vercel plainly that this is
a static site build, not a Python app, and there is no Python
entrypoint to find. A Python generator would have kept the
same confusion, because its build command is also Python.

## Local preview and build

From the repo root, with Node 20 or later:

```sh
npm install
npm run docs:dev
```

Then open the local URL VitePress prints, usually
http://localhost:5173/. That is the rendered site, not the
raw Markdown.

To check the production build, before you push:

```sh
npm run docs:build
npm run docs:preview
```

The build output is `.vitepress/dist/`, with `index.html`
from the root README, `SPEC.html` from the spec, and
`docs/` and `lib/` pages under their folders. That output
folder is not committed, it is built on every deploy.

## Vercel

One project only, rooted at the repo root. Delete the other
Vercel projects for this repo in the dashboard, especially
the `python` project, and any project rooted at `docs`.
Those are the projects that failed before, and no repo file
can make a Python library folder deploy as a web app.

Settings for the one remaining project, in the dashboard
or in the root `vercel.json`, which already sets them:

- Framework Preset: VitePress
- Root Directory: repo root, leave empty
- Install Command: `npm ci`
- Build Command: `npm run docs:build`
- Output Directory: `.vitepress/dist`

Deploy, then open the URL Vercel gives you. You should see
the rendered home page, with a sidebar for Spec, Docs, and
Libraries, and a search box. Redeploys happen on push to
`main` by default, when the project is connected to the repo.

The `lib/python/vercel.json` file is still in the repo,
with Git deployments disabled for a project rooted at that
folder, as a safety net in case that project is recreated.
It is not part of the Python package, `pyproject.toml` only
ships the `open_bookmarks` module.

## GitHub Pages

GitHub Pages is not set up for the VitePress build in this
repo yet. The old static route, serving `docs/` directly,
is gone with the old `docs/index.html`, which was deleted
in the follow-up PR that fixed the PR #2 review comments,
not in the original VitePress PR, where it was still on
`main` by mistake. Pages would need a build action that
runs `npm run docs:build` and publishes `.vitepress/dist/`,
which is a separate step, not done here. Do not set Pages
to serve `/docs` as it is now, that folder has no index
page of its own in the old static sense, its `index.md`
is rendered by VitePress into the site above.

## Any other static host

Not every static host works as-is, because this site uses
clean URLs: a page at `/SPEC` is really `SPEC.html` in the
output, with no extension in the URL. A host must map an
extensionless path to its `.html` file, like Vercel does
with `cleanUrls` in `vercel.json`, or with a rewrite rule.
If your host cannot do that, do not upload this output
unchanged, or every page except the home page will 404.
Instead, either use a host with clean URL or rewrite
support, or rebuild with `cleanUrls` set to false in
`.vitepress/config.mts`, which makes every page link end
in `.html`, and then upload that output. Run
`npm run docs:build`, then upload the contents of
`.vitepress/dist/` to the host you chose.
