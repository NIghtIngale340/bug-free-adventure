# Optional bundled fonts

Drop these files here and the app loads them automatically (`app/gui/theme.py::load_fonts`);
without them it falls back to Segoe UI / Noto Sans / DejaVu Sans and Consolas / DejaVu Sans Mono.

| Font | Use | Licence | Source |
|---|---|---|---|
| Inter (Regular, SemiBold, Bold `.ttf`) | UI text | SIL OFL 1.1 | https://rsms.me/inter/ |
| JetBrains Mono (Regular, Bold `.ttf`) | states, transitions, tape | SIL OFL 1.1 | https://www.jetbrains.com/lp/mono/ |

Not bundled in the repository because the files must be downloaded; check the licence file
into this folder together with the fonts.
