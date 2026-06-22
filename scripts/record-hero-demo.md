# Record README hero (`assets/hero-demo.mp4`)

B-primary storyboard: open on Pluto reactivity, brief Cursor chat for the cell edit, close on the updated plot.

Target: **~35s**, **1280×720**, **&lt;5 MB** H.264 MP4. Optional GIF via ffmpeg (see [Convert](#convert-to-gif-optional)).

## Before you record

1. Clean Pluto session (`stop_pluto_session` or restart Cursor with **pluto** MCP enabled).
2. `start_pluto_session` → open the demo notebook:
   - Dev: `examples/styx-demo.jl` in this repo
   - Installed plugin: `~/.cursor/plugins/local/styx/examples/styx-demo.jl`
3. `allow_execution` (or **Run notebook code** in Glass) so the slider and plot are live.
4. Verify **before** state on the plot cell (`3c4d5e6f-7081-4901-c234-56789abcdef0`):
   - `color=:red`
   - `title="sinc"`
5. Arrange layout: Glass wide; chat panel visible but not dominant until beat 2.
6. Hide notifications / disable Do Not Disturb.

## Shot list

| Time | Frame | Action |
|------|-------|--------|
| 0–8s | Glass full-width | Drag the range slider; plot window updates. No chat. |
| 8–12s | Glass + chat | **⌘⇧D** → click the **plot** cell (compute cell). |
| 12–18s | Glass + chat | Type/send: *Make the curve purple and set the title to "sinc (edited from Cursor)".* |
| 18–28s | Glass + chat | Let the agent stage + `submit_changes`; plot turns purple with new title. |
| 28–33s | Glass | Drag slider once more (reactivity still works). |
| 33–35s | Optional | Cut to install one-liner overlay or end on the plot. |

**After** state (agent should produce):

```julia
plot(sinc, lo, hi, color=:purple, xlabel="x", title="sinc (edited from Cursor)")
```

Re-run recording if the agent splits cells or leaves `pending_run` unstaged.

## Capture

**macOS (recommended):** QuickTime → File → New Screen Recording → crop to Agents window, or OBS with 1280×720 canvas.

**Tips:**

- Record at 2× resolution, scale down in post for sharper text.
- One continuous take; trim in QuickTime or ffmpeg.
- Keep cursor movement slow on the slider drag.

## Post-process

```bash
# Trim + compress (adjust -ss -to to your take)
ffmpeg -i ~/Desktop/styx-hero-raw.mov \
  -ss 0 -to 35 \
  -vf "scale=1280:720" \
  -c:v libx264 -crf 23 -preset slow -an \
  assets/hero-demo.mp4
```

Check size: `ls -lh assets/hero-demo.mp4` — aim under 5 MB. If larger, raise `-crf` to 26–28.

### Convert to GIF (optional)

```bash
ffmpeg -i assets/hero-demo.mp4 -vf "fps=12,scale=1280:-1:flags=lanczos" -loop 0 assets/hero-demo.gif
```

GIFs above ~10 MB are painful in git; prefer MP4 in README.

## Commit

```bash
git add assets/hero-demo.mp4 examples/styx-demo.jl README.md
# optional: assets/hero-demo.gif
git commit -m "Add Styx demo notebook and README hero video"
```

If MP4 is still too large for the repo, upload to a GitHub release or issue (`user-images.githubusercontent.com`) and point the README `<video src="…">` at the hosted URL.

## README embed

After `assets/hero-demo.mp4` exists, the README uses:

```html
<video src="assets/hero-demo.mp4" autoplay loop muted playsinline width="100%"></video>
```

GitHub renders repo-relative video paths once the file is on `main`.
