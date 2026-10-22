"""Wide-body impulse bars, 1-hour bars: a body over 80 % of the range with the range (in % of the high) above twice its 15-bar average goes long on an up close and short on a down close; a 0.3 % target and
1 % stop from the signal close (as fractions of the fill); reversing.
Port of FMZ strategy #442927 "Momentum Reversal Strategy Based on Multiple Timeframes" (mecha larga study).

FMZ source id: 442927

Source
    https://www.fmz.com/strategy/442927 (PineScript v5, FMZ last modified 2024-02-27 14:27:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-201), body > 80 %; range % > 2 x its 15-bar mean; tp 0.3 %, sl 1 %; RSI 14 (unused)
    Venta = body% > 80 and range% > 2 avg and close < close[1] -> entry short, exit(stop = close (1 + 1 %), limit = close (1 - 0.3 %))
    Compra = body% > 80 and range% > 2 avg and close > close[1] -> entry long, exit(stop = close (1 - 1 %), limit = close (1 + 0.3 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed percentage of the signal close: fixed fractions 0.01 / 0.003 of the fill
      (#437751); a new same-side signal while held moves the script's levels, which the port does not
      follow (as #439608). Both exits share the id "exit"; each entry's call re-binds it. The RSI is
      unused. A bar with no range has no body percentage (na). strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, wide-body impulse bars.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442927_wide_body_impulse_bar_pct_bracket"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "range_mult": [2.0, 1.5],
    "tp_pct": [0.003, 0.01],
}
DEFAULT_PARAMS = {"range_mult": 2.0, "tp_pct": 0.003, "sl_pct": 0.01, "body_min": 80.0, "avg_len": 15}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    rng = (h - lo).where(h > lo)
    body = (o - c).abs() / rng * 100
    force = ((h - lo) * 100 / h).abs()
    avg = force.rolling(int(p["avg_len"])).mean()
    imp = (body > float(p["body_min"])) & (force > avg * float(p["range_mult"]))
    lsig = (imp & (c > c.shift(1))).to_numpy()
    ssig = (imp & (c < c.shift(1))).to_numpy()
    s_, t_ = float(p["sl_pct"]), float(p["tp_pct"])
    ov = o.to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m:
            if ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
            elif lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
