# Deploy the docs

The docs are plain Markdown, with no build step, plus one HTML
entry page, `index.html`, in this folder. There are two supported
routes. Both are valid. Pick one.

## GitHub Pages

1. Push this repo to GitHub, with `docs/` on the `main` branch.
2. On GitHub, open the repo, then Settings, then Pages.
3. Under "Build and deployment", set Source to "Deploy from a branch".
4. Set Branch to `main` and Folder to `/docs`, then save.
5. Wait a minute or two, then open the Pages URL GitHub shows you.
   It will look like `https://svenkatreddy.github.io/open-bookmarks/`.

That is it. There is no build command to run and no extra config
file to add. When you push a change to a file in `docs/`, Pages
picks it up on the next deploy.

Note: GitHub Pages renders Markdown files, but links that point
outside `docs/` (for example to `../SPEC.md` in the repo root) will
not resolve on the published site in the same way they do on GitHub.
If that matters for a page, keep the link text plain and tell the
reader where the file lives in the repo, or copy the short version
of that content into the docs page itself.

## Vercel

Vercel is the second route, in the same repo, not a new repo. The
docs live in `docs/`, and Vercel serves that folder. There is no
separate docs package.

What Vercel does and does not do, honestly: Vercel serves static
files. It does not render Markdown to HTML on its own. The
`index.html` file in this folder is the readable home page on
Vercel. The other docs files, such as `SYNTAX.md` and
`EXAMPLES.md`, are served as Markdown files from the same folder,
which a browser shows as text. That is enough to read them, and
it is not the same as a rendered docs site. If a fully rendered
docs site is wanted later, that would need a static site
generator, which is out of scope for this preparation. Do not
claim that Vercel renders these Markdown files as HTML, because
it does not in this setup.

Steps, tested locally for the serving part, not yet deployed to
Vercel:

1. Push this repo to GitHub, with `docs/` on the `main` branch.
2. In Vercel, import the repo. Do not create a new repo for docs.
3. Set Framework Preset to Other. This is a static folder, not a
   framework project.
4. Set Root Directory to `docs`. This is the key setting. If you
   leave Root Directory at the repo root, Vercel will serve the
   repo root, not the docs folder.
5. Leave Build Command empty, and leave Output Directory empty.
   Vercel serves the Root Directory itself. The `vercel.json`
   file in `docs/` only sets clean URLs, it does not set the root
   or the output.
6. Deploy. Vercel will give you a URL for the project.
7. Open that URL. You should see the `index.html` home page.
   From there, the links to `SYNTAX.md`, `EXAMPLES.md`,
   `MONOREPO.md`, `DEPLOY.md`, and `versions.md` open those files
   as text.

Redeploys: Vercel redeploys on push to `main` by default, when the
project is connected to the repo. A change to a file in `docs/`
therefore updates the Vercel site on the next push, in the same
way as GitHub Pages.

## Local preview

To check the docs before you push, serve the docs folder from a
terminal:

```sh
cd open-bookmarks/docs
python3 -m http.server 8000
```

Then open `http://localhost:8000/` in a browser. You should see
the `index.html` home page. This serves the raw Markdown files
for the other docs pages, which is enough to check wording and
links. It does not render them like GitHub Pages does.

To check the whole repo, serve the repo root instead:

```sh
cd open-bookmarks
python3 -m http.server 8000
```

Then open `http://localhost:8000/docs/` in a browser.

## Any other static host

Any static host works, because there is nothing to build. Upload
the contents of `docs/` to the host, and serve `index.html` as
the home page. The Markdown files will be served as files, as
described for Vercel above, unless your host renders Markdown.

## Still needed before any Vercel publish

- A decision to publish docs on Vercel, from the repo owner.
- A Vercel account and a Vercel project connected to this repo,
  with Root Directory set to `docs` as above.
- A push to `main` after the project is connected, to trigger the
  first deploy.
