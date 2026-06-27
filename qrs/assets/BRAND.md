# QRS brand — palette & assets for plugin outputs

Use this so anything the skills generate (charts, exports) looks like QRS. Tokens
are from the canonical QRS Design System v1.0. **Charts use the navy + teal
data-viz pair — never rainbow palettes.**

## Logo

- `qrs-logo.svg` — vector mark (scalable; preferred).
- `qrs-logo.png` — raster, transparent corners (for charts / markdown / slides).

The mark: white italic serif **Q** on a dark-teal (`#1B3B3A`) rounded square.

## Color tokens

| Token | Hex | Use |
|---|---|---|
| ink-800 (primary dark teal) | `#1B3B3A` | Headings, dark grounds, logo field |
| ink-900 | `#0C0D0E` | Deepest background |
| teal-500 (accent) | `#5BBAB5` | Primary accent, markers, CTA fill |
| teal-600 | `#3C8481` | Hovers, secondary |
| teal-700 | `#29908A` | Borders/dividers; secondary chart line |
| navy-700 | `#324A6D` | **Primary data-viz line / axis stroke** |
| cream-50 | `#F4F6F6` | Light page / figure background |
| text-muted | `#69727d` | Captions, footnotes |
| white | `#FFFFFF` | Text on dark |
| status-ok / warn / error | `#22c55e` / `#f59e0b` / `#ef4444` | Operational / advisory / blocking |

## Chart recipe (matplotlib)

- Figure background `cream-50` `#F4F6F6`; axes background white.
- Primary series in `navy-700` `#324A6D`; secondary series in `teal-700` `#29908A`
  (dashed); highlight markers/bars in `teal-500` `#5BBAB5`.
- Titles in `ink-800` `#1B3B3A`; captions in `text-muted` `#69727d`.
- Grid: light, `alpha≈0.4`. No rainbow palettes, no drop shadows.
- Stamp `qrs-logo.png` small in a corner.

The bundled `cat-metrics` and `montecarlo` scripts already follow this recipe.

## Honesty note

Brand styling never changes a result's status. A sealed run is **UNSIGNED —
pre-release** until the KMS is live regardless of how a chart is colored, and a
local preview stays labeled "not the QRS engine, unsealed." Pretty ≠ validated.
