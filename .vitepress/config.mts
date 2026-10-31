// VitePress config for the open-bookmarks docs site.
// Source is the repo root, so the spec at SPEC.md, the README,
// and the pages under docs/ and lib/ are all rendered as one
// site, with the same relative links they already use on GitHub.
// No markdown file is moved for this site, and no frontmatter
// is added to existing pages, so they stay readable on GitHub
// exactly as before. VitePress only renders them.
import { defineConfig } from "vitepress";

export default defineConfig({
  title: "open-bookmarks",
  description:
    "A simple, open format for sharing bookmark packs: plain JSON folders and links, no account, no server.",
  cleanUrls: true,
  // README.md files are the index page of their folder on
  // GitHub, and on this site too. Without this, the root
  // README would build as /README, and the site home / would
  // be a 404.
  rewrites: {
    "README.md": "index.md",
    "lib/js/README.md": "lib/js/index.md",
    "lib/ts/README.md": "lib/ts/index.md",
    "lib/python/README.md": "lib/python/index.md",
  },
  // One link that is valid for local use, but is not a site
  // page: the local dev URL in DEPLOY.md. LICENSE and
  // packs/examples/ links are now hosted GitHub URLs, not
  // relative links, so they are not checked as dead links,
  // and they work on the built site, where VitePress does
  // not copy non-Markdown files into the output.
  ignoreDeadLinks: [/^https?:\/\/localhost/],
  themeConfig: {
    nav: [
      { text: "Home", link: "/" },
      { text: "Spec", link: "/SPEC" },
      { text: "Docs", link: "/docs/" },
      { text: "GitHub", link: "https://github.com/svenkatreddy/open-bookmarks" },
    ],
    sidebar: [
      {
        text: "Format",
        items: [
          { text: "Home", link: "/" },
          { text: "Spec", link: "/SPEC" },
          { text: "Changelog", link: "/CHANGELOG" },
        ],
      },
      {
        text: "Docs",
        items: [
          { text: "Docs home", link: "/docs/" },
          { text: "Syntax", link: "/docs/SYNTAX" },
          { text: "Examples", link: "/docs/EXAMPLES" },
          { text: "Monorepo", link: "/docs/MONOREPO" },
          { text: "Deploy", link: "/docs/DEPLOY" },
          { text: "Versions", link: "/docs/versions" },
        ],
      },
      {
        text: "Libraries",
        items: [
          { text: "JavaScript", link: "/lib/js/" },
          { text: "TypeScript", link: "/lib/ts/" },
          { text: "Python", link: "/lib/python/" },
          { text: "JavaScript publishing", link: "/lib/js/PUBLISHING" },
          { text: "Python publishing", link: "/lib/python/PUBLISHING" },
        ],
      },
    ],
    search: {
      provider: "local",
    },
    socialLinks: [
      { icon: "github", link: "https://github.com/svenkatreddy/open-bookmarks" },
    ],
  },
});
