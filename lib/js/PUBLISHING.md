# Publishing the Node package, not yet published

This package is prepared, not published. Do not run the publish
commands below until the format 1.0 publication is decided and the
package name is confirmed at publish time. The package version is
0.1.0, while the format is 1.0 Draft, because the package itself
has not had a 1.0 release yet. When the format is published, the
package version can move to 1.0.0 in a separate release, or stay
on its own version line with a note in the changelog. The two
versions are related, not identical: the format version lives in
the format field of every pack, the package version lives in
package.json.

## What is published

From `lib/js`, the files listed in package.json: the library
`open-bookmarks.mjs`, its type declarations
`open-bookmarks.d.ts`, this README, the example, and this file,
plus the encryption entry point `./encrypt`, with
`encrypt.mjs`, `encrypt.d.ts`, and `encrypt-example.mjs`.
No other files from the repo are included in the npm package.

Install, after publication, from a project that uses the
package:

```sh
npm install open-bookmarks
```

Then, in code, the main entry point is `open-bookmarks`,
and the encryption entry point is `open-bookmarks/encrypt`:

```js
import { loadPack } from "open-bookmarks";
import { encryptPack, decryptPack } from "open-bookmarks/encrypt";
```

The second import works only after publication. Until then,
use the repo-relative file `lib/js/encrypt.mjs` directly.

## Recommended route: OIDC trusted publishing

The recommended route is npm trusted publishing with OIDC, so no
long-lived npm token has to be stored. That setup is done once in
the npm package settings and in the repo, by the package owner,
and it is not part of this repo. The steps below assume that
setup is in place, or that you are publishing by hand with a
login, as a fallback.

## Publish by hand, manual step

From the repo root, or from `lib/js` with the package.json there:

```sh
cd lib/js
npm login
npm publish --access public
```

Check the publish first, without publishing:

```sh
npm publish --dry-run
```

That dry run lists the files that would be included. If the list
does not match the files section in package.json, stop and fix
package.json first.

After a successful publish, check the package page on npm, and
update the README install section to remove the "not yet
published" note. Do not publish from a branch other than main
unless you mean to publish a pre-release, and do not publish a
version that is already on npm.

## Still needed before any publish

- A decision to publish, from the repo owner.
- An npm account with publish rights for the name
  "open-bookmarks", or a scoped name if that name is taken at
  publish time.
- Either OIDC trusted publishing set up, or a login for the
  manual route above.
- A check that the package version in package.json has not
  already been published.
