"""Body price channel touches (AlexInc), 1-hour bars, with close_all on every bar: two bars in a row with the low under the
13 % line of the 20-bar body channel go long, two highs over the 87 % line go short; every position is closed on the bar
after its fill.
Port of FMZ strategy #431502 "Donchian Channel Breakout Trading Strategy" (AlexInc PriceChannel Str).

FMZ source id: 431502

Source
    https://www.fmz.com/strategy/431502 (PineScript v3, FMZ last modified 2023-11-08 12:31:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 212-291), channel 20 on bodies, 13 %, stop option off (commented out)
    pcmax / pcmin = highest(max(open, close), 20) / lowest(min(open, close), 20); yl = pcmin + 13 % range; yh = pcmin + 87 %
    upsign = low < yl on this and the previous bar -> entry long;  dnsign = high > yh on both bars -> entry short
    if true: close_all (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * close_all on every bar acts on the position held at the start of the bar: a position entered on
      a signal bar fills at the next open and is closed at that bar's close; the bar it closes takes
      no new position (as #430853): one-bar holds as written. The stop levels are only plotted (the
      exits are commented out). The short's qty na is the default size.
    * strategy.entry reverses: REVERSAL INTENDED. The 2018-2100 window is dropped. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close_all every bar as written.
    2 generic: PASS, a channel on bodies and its percentage lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital % lot stored in original_sizing.txt.
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

NAME = "fmz_431502_body_channel_one_bar"
FAMILY = "channel_reversal"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "history": [20, 40],
    "pct_dev": [13, 25],
}
DEFAULT_PARAMS = {"history": 20, "pct_dev": 13}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["history"])
    pmax = np.maximum(o, c).rolling(n).max()
    pmin = np.minimum(o, c).rolling(n).min()
    d = float(p["pct_dev"])
    yh = (pmax - pmin) / 100 * (100 - d) + pmin
    yl = (pmax - pmin) / 100 * d + pmin
    bd, bu = (lo < yl), (h > yh)
    up = (bd & bd.shift(1, fill_value=False)).to_numpy()
    dn = (bu & bu.shift(1, fill_value=False)).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0:
            pos = -1 if dn[i] else (1 if up[i] else 0)
        else:
            pos = 0                                      # close_all on every bar
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
