# Claude Code for research work

Drawn from my own sessions (15 projects, ~250 MB of transcripts). Scope note: this
is about **what is specific to working with Claude** — how to ask, what it is good
and bad at, and what it costs. Things that are just good practice anyway (LaTeX, Slurm, 
figure style, writing) get a pointer.

---

## The one idea

> **If a task can be scripted, get Claude to write the script — then let the
> script run.**

1. **The script is the artifact; the chat is not.** A conversation can't be re-run
   in six months. Scripted behaviors are reproducible.
2. **Anything I explain twice goes in `CLAUDE.md`.** Brief Claude on a project to 
   generate a CLAUDE.md as a fact sheet with manual proofreading. That is what lets one project
   run from development → deployment → analysis → writing without re-briefing.
3. **Version control and data backups** Make sure you know what Claude has changed 
   and note the 3-2-1 backup strategy. Transferable skills from pre-AI era.

---

## Agenda

| # | Topic |
|---|---|
| 1 | Coding and numerical debugging — **demo A** |
| 2 | Job monitoring: script + cron — **demo B** |
| 3 | Literature review: Claude writes the script *and* its input |
| 4 | Plotting: "here's the data, here are the axes" |
| 5 | Writing: outline → section → close edit |
| 6 | Slides and SVG diagrams |
| 7 | Context and cost |

Each demo has its own directory — `demo_A/` and `demo_B/` — and that is where to
start the session, so Claude sees nothing but the demo. Neither touches a real
campaign, a cluster, or my Zotero library. Both have been run once and captured
in `transcripts/` — see `transcripts/README.md` — so either can be presented from
the recording if the live version won't cooperate. The transcripts sit *outside*
the demo directories on purpose: they contain the answers.

The `.md` files this handout points at are copied into `md/` — see
`md/README.md` — so nothing here depends on my home directory.

---

## 1. Coding and numerical debugging

- **Ask for the mechanism, not the patch.** "Which line produces the first bad
  number, and why" is answerable and checkable; "fix the crash" is not. Similar
  for applying new feature and tests.
- **Keep the boundary explicit.** A phrase I reuse: *"focus on the logistics and
  code"* — the automation is welcome, the physics judgement is mine.
- **Example — a spurious wave in the outer dust density** of a TriPoD disk-buildup
  run (`genga_tripodpy/tripodpy_nbod_disk_buildup`), at t ~ 8x10^5 yr:
  - **`CLAUDE.md` carried the code structure**, so the hunt started from a map
    rather than a grep: which module owns the infall source terms, which updater
    runs in which hook, where the dust floor is hardset.
  - **Two suspects, both wrong.** A singularity in the code and the floor value.
    One test run each; both came out *identical* to the baseline. A suspect cleanly
    eliminated is a result, not a wasted run.
  - **The third hypothesis was the one that made a prediction.** 
    Rerunning at `rmax=1000 au`. Confirmed, and the fix is just extending rmax.
  - Each hypothesis became **a script in `tests/`** plus one comparison plotter,
    so the whole chain re-runs on demand — and the answer went back into
    `CLAUDE.md` so the next session starts from the conclusion.
  - **What it cost.** ~20 min of my time (8 prompts, 273 words — two of which
    were the single word `status`), ~30 min of Claude actually working, and
    23.7 h of CPU across the four test runs. The bottleneck was never the
    thinking; it was four 6-hour simulations, and I did not had to sit and watch them.

**→ Demo A**: a generic NaN, diagnosed from the output file.

---

## 2. Job monitoring — script plus cron

**The Claude-specific: the division of labour.** Claude wrote the scripts;
**cron runs them.** Claude just reads the output and makes decisions (agentic) if needed:

```cron
0 */2 * * * /usr/bin/flock -n /tmp/sol_sys.lock  ~/output/sol_sys/rsync_and_plot.sh --once  >> ~/output/sol_sys/rsync_and_plot.log 2>&1
```
Prompts that produced this class of script:

> "monitor this test and keep track of the giant planet. If all giant planets are lost, kill the test and notify me"

**→ Demo B**: a read-only status script, then cron. Listing under *Demos*.

---

## 3. Literature review

> **ADS** API (`api.adsabs.harvard.edu`) for search, **Zotero** Web API v3 
> via `pyzotero` for the library. Ten minutes with the docs and Claude writes that client.

**The Claude-specific part is that it writes the script's *input*, not just the
script.** I paste a paragraph of my own prose:

> *"…Ophiuchus, which is ∼1–2 Myr (Luhman & Rieke 1999; Wilking et al. 2005) …"*

and it emits the resolver's input file with **disambiguating keywords it supplies
from domain knowledge**:

```
Preibisch et al. 2002::Upper Scorpius OB association age low mass stellar population
```

That topic string is what makes matching work at all. Same trick from the other
end: paste the paper outline, get back which references are already in the library
and which are missing.

---

## 4. Plotting

**The pattern: say where the data are and what the axes are.**

> "x: semi-major axis [AU], log, fixed [0.01, 20]; y: planet mass [M_earth], log,
> fixed [1e-3, 1e3]; for the selected (M_star, alpha, t_0, tau_dep) plot all 15
> sims at the current frame, colour by Z, one legend entry per Z"

**It works out the format itself** — this is the part that saves real time. It
found the Fortran `1d-4` exponent notation in a parameter file, and
reverse-engineered an unformatted binary layout from the Fortran source to replace
a slow reader with a one-pass Python scanner, then validated it against the
original output. Reflecting on my own workflow: don't take anyone's words on data
format, read the source code.

**Apply style for all plots through markdone**
> Figure style (journal column widths, fonts, tick direction) isn't Claude-specific
> — mine is one `rcParams` block in `~/ms/writing.md`. Point it there once.

### Honest negatives

That dashboard took **~15 correction rounds**: invisible plots, a too-narrow
selector, then the kernel dying on memory twice. It only became sound when I said
*"move this process to a separate script and store the results"*.

---

## 5. Writing

> Not Claude-specific: my prose and number conventions are in `~/ms/writing.md`
> (Results describe, Discussion interprets). Let Claude take over the LaTeX pains.
> I write with VS Code and the LaTeX Workshop extension, use Overleaf's git integration.

Three things that *are* about working with Claude:

**1. Outline first, as scaffolding you own.**
Iterate with Claude on the outline, not too different from my usual writing procedure.

**2. One sentence per line.**

> "turn the tex file to one line per sentence for easier manual editing"

Diffs become per-sentence, and my edits and Claude's stop colliding on the same line.

**3. The review line — this is what makes parallel work safe.**

```
------ review line ------
```

> "for all edits, apply directly after the review line, but ask me first for
> things before the review line"

Above it is reviewed text; below it is draft. The line moves down as I review. So
Claude can draft §4 or edit plots while I close-edit §3, and it never silently rewrites
something I've already signed off.

**"No interruptions":** across my sessions the permission mode was
`auto` 4722 times vs `default` 66 — essentially no prompts. That is what makes long
unattended stretches work: one project ran as a *single session* for seven weeks,
and another picked up after a 16-day gap. Run it in `tmux`.

---

## 6. Slides and SVG diagrams

**Let Claude write a small generator script that makes SVG diagrams**. The
geometry is computed rather than eyeballed, and re-running it is free and defined.

Two things make it actually pleasant:

- **Named groups.** The generator emits `<g inkscape:label="core">`,
  `"envelope"`, `"arrows"`. I then opened the file in Inkscape, deleted what I
  didn't want, and said *"I have removed all unnecessary elements"* — and Claude
  patched **only** the group I asked about, preserving my edits. After that,
  one-liners work: *"delete the scalebar group"*, *"remove the black edge"*,
  *"make the core smaller and the envelope thinner"*.
- **Measure the source, don't guess.** Asked to reuse half of a published figure,
  it located the panel dividers and the sphere centre numerically from the pixels,
  and counted the arrows by flood-fill, before rebuilding it as vector.

**The verification loop is the habit worth teaching:**

```
compile → grep the log → render ONE page at low DPI → actually look at it
```

---

## 7. Context and cost

### Filling context window is not necessarily bad

Maintain high signal-to-noise, and misleading context is actively harmful. But:

1. **It isn't free.** Every turn re-sends the whole conversation. Cached reads cost
   0.1× fresh input, which is cheap per token but multiplied by every turn: one of
   my sessions logged **193 M cache-read tokens** — the equivalent of ~19 M fresh
   input tokens — against only 0.5 M tokens of output.
2. **Retrieval degrades with distance.** A relevant fact 500 k tokens back is not
   as good as the same fact nearby. Long context is supported, not free of cost to
   quality.
3. **Useful info decays into misleading info.** Context has
   no timestamps and no invalidation, so *your own criterion is a moving target*.
   Nobody added noise; a true statement simply stopped being true.

**So: treat context as a cache.**

| Instead of | Do |
|---|---|
| letting one session sprawl across unrelated tasks | `/clear` between tasks |
| relying on a fact stated 300 turns ago | put durable facts in `CLAUDE.md`; re-check mutable state |
| reading a haystack into the main session | hand it to a **subagent** — it reads, you get the needle |
| guessing where the tokens went | `/context all` |

*(Preparing this handout: four subagents read ~250 MB of transcripts; none of that
raw text entered the main session.)*

### Minimise usage by avoiding PDFs

**PDFs really are expensive:** every page is sent as an image *and* as text —
1500–3000 text tokens **plus** up to 4784 image tokens *per page*. A 30-page PDF can
approach a quarter of a 1 M window before anyone speaks.

---

### One slide of rules

0. Version control and data backup. More important in post-AI era.
1. If you explain it twice, it goes in `CLAUDE.md`.
2. A wrong `CLAUDE.md` is worse than none.
3. Read-only tool first, mutating tool second, `--dry-run` on both.
4. Ask for the mechanism, not the patch.
5. Never write a number you haven't just computed.
6. Context is a cache.

---

## Not covered here

Everything above is what I actually use daily. Three things I have *not* used
enough to share, flagged so nobody thinks they don't exist:

- **Skills** — a folder (`.claude/skills/<name>/SKILL.md`) holding instructions
  Claude loads **on demand**, not every session the way `CLAUDE.md` does; also
  how you define your own `/slash-command`. Where to draw the line: **a skill
  for the procedure, `CLAUDE.md` for the invariant** — a skill only fires when
  something invokes it, so anything that must never be missed stays in
  `CLAUDE.md`.
- **Remote control** — driving a session from another device, e.g. checking on a
  long run from a phone. Relevant to the job-monitoring topic; I still use `tmux`
  due to account policy restrictions.
- **Chrome extension / Claude in the browser** — letting Claude drive a real
  browser page. Would matter for anything web-based (journal submission portals,
  ADS by hand).

---

## Demos
### Demo A - A generic numerical bug, found in the output file

Start the session in `demo_A/`:

```bash
cd demo_A && claude
```

```bash
python3 demo_drag.py     # six dust grains relaxing to the gas velocity under drag,
                         # explicit Euler, one shared dt -> writes demo_drag_out.npz
```

It prints `final max|v| = 4.150e+180`, plus a couple of numpy overflow warnings
that tell you *that* it broke and nothing about where. That is all you normally
get. Then, instead of adding prints, ask:

> "demo_drag_out.npz ends with a velocity of 4e180. Find where it stops making
> sense and tell me the mechanism, not just the fix."

The whole answer is one ratio, which is why this works live. Each step is just
`v <- v * (1 - dt/t_stop)`, so the step multiplies the velocity by
`A = 1 - dt/t_stop`, and the scheme is stable only while `|A| <= 1`, i.e.
`dt <= 2*t_stop`. With one shared `dt = 0.3`:

| `t_stop` | `dt/t_stop` | `A` | what the grain does |
|---|---|---|---|
| 0.05 | 6.0 | **-5** | flips sign and grows x5 every step, from step 1 |
| 0.10 | 3.0 | **-2** | flips sign and grows x2 every step |
| 0.20 | 1.5 | -0.5 | flips sign but *decays* — harmless |
| 0.5 - 2.0 | < 1 | +0.4 to +0.85 | decays smoothly, as it should |

**Points to make:**

- It stops making sense at **step 1**, not at the overflow 439 steps later. The
  smallest grain goes `1, -5, +25, -125, …` — you can read the bug off the
  numbers without any analysis.
- **Oscillation alone is not the bug.** The `t_stop = 0.2` grain also flips sign
  every step and is perfectly fine. `|A| > 1` is the bug.
- Only the two best-coupled grains are broken; the rest of the run looks healthy.
  That is how this bites in a real dust code — a global `dt` chosen without
  checking the most restrictive cell.
- **It got a number wrong.** It attributed the `4e180` to the smallest grain; that
  value is actually `2^600` from the *second* grain, because the smallest one
  overflowed to `nan` at step 440 and `nanmax` skipped it. The mechanism was
  right and checkable in 48 s — the arithmetic around it still needed checking.
  Rule 5, live.

### Demo B - a read-only status script, then cron

Start the session in `demo_B/`:

```bash
cd demo_B && claude
```

```bash
./demo_connect.sh status     # read-only: is the tunnel up?
./demo_connect.sh up         # the mutating half — re-dials up to 10x, has --dry-run
./demo_status.sh             # read-only: the Slurm queue, over ssh
```

`demo_status.sh` prints running/pending counts, pending reasons, and jobs by
name, and by construction it *cannot* change cluster state — it runs `squeue`
and nothing else, and everything needing `sudo` lives in `demo_connect.sh`
instead. That split is the design rule from §2, made visible.

There is no offline mode: it always goes over ssh, so **the tunnel has to be up
first**. That is not a limitation to apologise for on stage — it is the demo.
Without the VPN it fails in ~20 s (`BatchMode=yes` so it never waits on a
password, and a hard `timeout` because `ConnectTimeout` applies per resolved
address and a dual-stack host will otherwise hang past it) and says which script
to run next.

The starting prompt for the session:

> "Two scripts here. `./demo_status.sh` is read-only and reports the Slurm queue
> over ssh. `./demo_connect.sh {status|up|down}` is the only thing allowed to
> touch the WireGuard tunnel.
>
> Tell me whether my jobs are still running. If the cluster is unreachable,
> check the tunnel, bring it up if it is down, then retry once. Put the tunnel
> back down when you are finished. Do not submit, cancel, or modify any job, and
> do not edit either script."

Then show the one line that makes it autonomous:

```cron
*/30 * * * * /usr/bin/flock -n /tmp/demo_status.lock ~/…/demo_status.sh >> ~/demo_status.log 2>&1
```

#### The VPN, and why `sudo` is the hard part

See https://doku.lrz.de/vpn-eduvpn-openvpn-konfiguration-erzeugen-11497395.html for eduVPN config,
MWN Split-Tunnel (Standard, Wireguard) used below.

The cluster is only reachable through VPN, so anything unattended has to be
able to bring the tunnel up itself. `wg-quick` needs root, and cron has nobody to
type a password at — so one narrowly scoped `NOPASSWD` rule in
`/etc/sudoers.d/` (edit with `sudo visudo -f`, never a plain editor):

```
tommy ALL=(ALL) NOPASSWD: /usr/bin/wg-quick up lmu-vpn, \
                          /usr/bin/wg-quick down lmu-vpn, \
                          /usr/bin/wg show
```

Three exact commands on one named interface — not `NOPASSWD: ALL`, and not
`wg-quick` with free arguments. `sudo -l` prints what is actually in effect; check
it rather than trusting the file.

Then the script can test-and-connect:

```bash
sudo wg show | grep -q "latest handshake:" || {   # already up?
    sudo wg-quick down lmu-vpn                     # clear a half-open tunnel
    sudo wg-quick up   lmu-vpn
}
```

**Points to make:** (i) Claude wrote it in one prompt from a description of what I
wanted to see; (ii) **cron runs it, Claude doesn't** — no tokens, no session, no
3 a.m. babysitting; (iii) `flock -n` stops cycles overlapping; (iv) it is read-only
by construction, which is why it's safe to automate at all.

And (v): **the log is the handover.** Cron appends to `demo_status.log` all night
for free; in the morning you ask one question:

> "read demo_status.log — what changed overnight? When did jobs start or finish,
> and is anything pending for a reason I should care about?"

That is the whole division of labour in one line. Nothing is watching the queue on
your behalf at 3 a.m., and nothing needs to be — the schedule belongs to cron, the
reading belongs to Claude, and you pay for the reading once, when you actually
want an answer. A night of two-hourly cycles is a couple of hundred lines of
append-only text, which is a cheap thing to hand over and a miserable thing to
read yourself.