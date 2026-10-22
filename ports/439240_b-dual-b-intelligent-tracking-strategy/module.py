"""Bollinger trend and counter-trend entries on ohlc4 (20, 2), 1-hour bars: a red bar closing between the basis and the upper band, or a close at or under the lower band, goes long; the mirror goes short; a long
closes on a green bar, a short on a red bar with a body over half its 30-bar average.
Port of FMZ strategy #439240 "双B智能追踪策略Dual-B-Intelligent-Tracking-Strategy" (Noro's Bollinger Strategy v1.2).

FMZ source id: 439240

Source
    https://www.fmz.com/strategy/439240 (PineScript v3, FMZ last modified 2024-01-18 15:41:20).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 149-202), long and short on; Bollinger 20, mult 2, source ohlc4; trend and counter-trend entries on; date inputs unused
    up1 = red and basis <= close < upper and (close < avg price or flat);  dn1 = green and lower < close <= basis and (close > avg price or flat);  up2 = close <= lower;  dn2 = close >= upper
    exit = (long and green) or (short and red) and body > ema(body, 30) / 2;  if up1 or up2: entry Long;  if dn1 or dn2: entry Short;  if exit: close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is read with Pine's precedence: (long and green) or (short and red and big body). The
      average price is the fill open of the position held at the bar close. The final close_all acts on
      the position held at the bar close and the bar ends flat (as #430380); from flat the exit cannot
      fire and the signal opens. A same-side signal while in a position is ignored; when both sides
      signal, the later short entry wins (as #437773). REVERSAL INTENDED. The default size is sizing.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands, bar colours and bodies.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND433588 (2 members, best partner #433588, Jaccard 0.681); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439240_noro_bollinger_ohlc4_colour_exit"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.0, "body_len": 30}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    src = (o + h + lo + c) / 4
    n = int(p["length"])
    basis = src.rolling(n).mean()
    dev = float(p["mult"]) * src.rolling(n).std(ddof=0)
    upper, lower = (basis + dev).to_numpy(), (basis - dev).to_numpy()
    bv, cv, ov = basis.to_numpy(), c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    body = (c - o).abs()
    big = (body > body.ewm(span=int(p["body_len"]), adjust=False).mean() / 2).to_numpy()
    green, red = cv > ov, cv < ov
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, avg = 0, np.nan
    for i in range(m):
        flat = pos == 0
        up1 = red[i] and bv[i] <= cv[i] < upper[i] and (flat or cv[i] < avg)
        dn1 = green[i] and lower[i] < cv[i] <= bv[i] and (flat or cv[i] > avg)
        up = up1 or cv[i] <= lower[i]
        dn = dn1 or cv[i] >= upper[i]
        ex = (pos == 1 and green[i]) or (pos == -1 and red[i] and big[i])
        new = pos
        if up and pos != 1:
            new = 1
        if dn and new != -1:
            new = -1
        if ex:
            new = 0
        if new != pos and new != 0:
            avg = ov[i + 1] if i + 1 < m else np.nan
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
