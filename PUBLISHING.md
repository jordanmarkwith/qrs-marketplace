# Publishing the QRS marketplace

This folder **is** the marketplace repo. Push it to a public git host and anyone
can install the `qrs` plugin from it. No build step.

## 1. Push to GitHub (one time)

```bash
cd qrs-marketplace
git init -b main
git add .
git commit -m "QRS plugin marketplace v1.0.0 (qrs v0.1.1)"
# create an EMPTY public repo named qrs-marketplace on GitHub first, then:
git remote add origin https://github.com/YOUR_GH_USER/qrs-marketplace.git
git push -u origin main
```

The repo must be **public** for anyone to install (for a private/team rollout,
just grant collaborators access — the same commands work).

## 2. Tell people how to install

```
/plugin marketplace add YOUR_GH_USER/qrs-marketplace
/plugin install qrs@qrs-risk
```

- `qrs-risk` is the marketplace id; `qrs` is the plugin id (so `qrs@qrs-risk`).
- The plugin shows up as **QRS** (its `displayName`).
- `/plugin marketplace add` also accepts a full URL or a local path.

## 3. Shipping updates

1. Edit the plugin under `qrs/` (e.g. a skill).
2. Bump the version in **both** places so they agree:
   - `qrs/.claude-plugin/plugin.json` → `"version"`
   - `.claude-plugin/marketplace.json` → the `qrs` entry's `"version"`
   (The `claude plugin tag` command validates that these two agree and creates a
   `qrs--vX.Y.Z` release tag if you want tagged releases.)
3. Commit and push.
4. Users refresh with:
   ```
   /plugin marketplace update qrs-risk
   /plugin update qrs
   ```

## 4. Validate before you push

```bash
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate qrs/.claude-plugin/plugin.json
```

Both should report ✔ (they do as shipped).

## Notes

- **Layout:** the plugin is embedded here (`"source": "./qrs"`), so this is a
  single self-contained repo — nothing else to host. If you'd rather keep the
  plugin in its own repo later, change the entry's `source` to a `github`/`git`
  source pointing at that repo.
- **Free vs sealed:** the free local skills (`cat-metrics`, `grounded`,
  `montecarlo` local preview) work for every installer immediately. Sealed runs +
  the upgrade funnel stay gated until you bring the engine online:
  1. serve the sample-and-seal mode at `https://api.qrsrisk.com/mcp` (the
     `qrs-oracle` connector in `qrs/.mcp.json`),
  2. activate the seal KMS (seals are UNSIGNED — pre-release until then),
  3. flip the metered free-run quota / billing from test to live.
  Until then the plugin honestly says "sealed runs coming online" — nothing fakes
  being live, which protects the QRS brand.
- **Token:** never commit a `QRS_API_TOKEN`. It's per-user, supplied via the
  environment (see `qrs/CONNECTORS.md`).
