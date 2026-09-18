# Writing and plotting conventions

## 1. Numbers

**Never write a number you have not just computed.** Every quoted value in the
manuscript was checked against the data with a throwaway script. Keeping those
scripts is worth it: figure selections and cuts change, and a number that was
right in June is wrong in August.

**Always state the subset.** The single most common error was a correct number
attached to the wrong population.

**Quantify every vague adjective.** "Uniform", "negligible", "much larger" all
got sent back. Replace with the measured spread and say what sets the extremes:
*"the largest spread between bodies is 5.4%, for CO in the r₀ = 75 au run"*.

**Ranges versus worst cases.** Do not pair a range over the sample with a single
worst case in the same clause — it reads as a per-object ratio and is not one.
Either give the per-object ratio range, or give both extremes with the object
that sets each.

**Check the arithmetic of your own claims.** "At least a factor of seven" was
written when the minimum was 6.6. Compute the bound, do not eyeball it.

**Distinguish measurement from estimate from attribution.** Say "we attribute
this to…" when the mechanism is inferred rather than measured. State the
direction of any bias, and whether a bound is an upper or lower limit.

---

## 2. Prose

**Keep result section descriptive.** only make interpretations in discussion section.

**American spelling for AAS journal.** vapor, modeling, favor, behavior, normalization.

**Tense.** Past for what was done ("we ran", "the timestep was set"); present
for what a figure or result shows ("Fig. 3 splits…", "the ices record…").

**Results describe, Discussion interprets.** Results carries measurements and
cross-references forward (`Sect.~\ref{sec:dis:...}`); causal clauses,
mechanisms and implications live in the Discussion. Strip "because", "since",
"therefore" from Results and check whether what remains is still a measurement.

**Section openings.** The Results opening is a roadmap only — what comes in
which subsection — with no data. Put the run statistics at the head of the
first subsection that uses them.

**Say what the work does not show.** Keep an explicit list, so nothing reads as
excluded when it is merely untested. "Neither supported nor excluded by these
simulations" is a real result and worth stating.

---

## 3. Figures

### Geometry and style

```python
SINGLE, DOUBLE = 3.5, 7.1        # in, AASTeX column widths — set exactly
THIN = 0.55                      # data line width
plt.rcParams.update({
    'font.size': 8, 'axes.labelsize': 8, 'axes.titlesize': 8,
    'xtick.labelsize': 7, 'ytick.labelsize': 7, 'legend.fontsize': 6.5,
    'axes.linewidth': 0.7,
    'xtick.direction': 'in', 'ytick.direction': 'in',
    'xtick.top': True, 'ytick.right': True,
    'text.usetex': True, 'font.family': 'serif',   # matches the manuscript
    'pdf.fonttype': 42,
    'savefig.bbox': 'standard',                    # keep the requested size
    'figure.constrained_layout.use': True,
})
```

Height is computed from content (e.g. `0.118 * n_rows + 1.2`) so panels stay
legible as the sample grows. Check the output page size to confirm a layout
change actually took: 4 panels at 7.40 in is 532.8 pt, 3 panels at 5.55 in is
399.6 pt.

### Axis choices

- Use a **linear** axis when "absent" must be distinguishable from "small":
  a species at exactly zero is visible at 0 on a linear axis and falls off a
  log axis entirely. Add a small negative margin so the zero markers clear the
  spine.
- Use **log** when the range is decades. Say in the caption that a species with
  no marker is below the plotting range.
- Mark a floor explicitly, and fade any part of a curve that sits on it — a
  ratio built from a floored density is an upper limit, not a measurement.

### Panels and legends

- Panel letters **inside** the axes, in whichever corner the data leaves free;
  they need not be in the same corner in every panel.
- Order panels to match the order the text discusses them.
- Multi-panel legends: `loc='outside upper center'` with an explicit `ncol`.
- With `sharey`, do not clear tick labels with `set_yticklabels([])` — it clears
  the shared axis. Use `tick_params(labelleft=False)`.
- Build legend handles as explicit proxies, not by harvesting from the axes: a
  species can be absent from a whole panel and would then have no handle,
  silently shifting the legend.

### Generation

- One script generates all figures, with a CLI for selective regeneration
  (`make_figures.py composition c_over_o`), substring matching, and per-figure
  keyword overrides.
- **Name files by content, not number** (`disk_zones_r75.pdf`, not `fig4.pdf`),
  so renumbering the paper does not rename files.
- Keep hand-picked epochs in one table, shared between the disk-snapshot figure
  and the time-series figures, so their vertical guides cannot drift apart.
- Move unused figures to `fig/archive/` rather than deleting them.
- **Verify visually.** Render with `pdftoppm` and look at it. The code running
  without error says nothing about whether a label is legible, a marker is
  hidden, or a panel letter overlaps the data.

---

## 4. Manuscript mechanics

**Bibliography.** The `.bib` is Zotero-synced — never hand-edit it. Check a key
exists before citing it (`grep '^@[a-z]*{Key,'`); a citation to a missing key
silently degrades the whole bibliography. Watch for near-duplicate keys from
different first authors: `Liu2018` (pebble accretion) and `Liu2019a` (Jupiter
giant impact) are unrelated papers.

**Building.** One step per command, and check the intermediate:

```
rm -f aas.aux aas.out
pdflatex -interaction=nonstopmode aas.tex
bibtex aas                 # then check aas.bbl is non-empty
pdflatex -interaction=nonstopmode aas.tex
pdflatex -interaction=nonstopmode aas.tex
```

Chaining these with `;` or `&&` caused most of the build failures in this
project: `bibtex` running against a half-written `.aux` truncates `.bbl` to
zero bytes, which then presents as hundreds of undefined citations and a
mysteriously short document. A corrupt `.aux` shows up as `Text line contains
an invalid character` with `^^@` on line 1 — delete the `.aux` and start over.

**Do not run `pdflatex` while an editor's `latexmk` is watching the file.** Two
builds racing on the same `.aux` produced every one of those failures.

**Checking that an edit landed.** Read the `.tex`, not the PDF — the PDF may
predate the edit. When checking rendered text, flatten whitespace first, since
`pdftotext` wraps lines and breaks multi-word patterns:

```bash
pdftotext aas.pdf - | tr '\n' ' ' | tr -s ' ' | grep -c "phrase to find"
```

**Review line.** A literal `------ review line ------` marker in the source
separates reviewed text from draft. Edit freely below it; ask before touching
anything above. Move it down as review progresses.
