"""Noro's colour-bar fades, 1-hour bars: a red bar with a body over its EMA 30 goes long, a green bar with a body over it
goes short; a bar of the trade's own colour (green for a long, red for a short) closes the trade when it is in profit
against the fill price.
Port of FMZ strategy #432354 "基于K线实体的多空策略Candlestick-Body-Based-Dual-Thrust-Strategy" (Noro's ColorBar Strategy v1.0).

FMZ source id: 432354

Source
    https://www.fmz.com/strategy/432354 (PineScript v3, FMZ last modified 2023-11-16 17:14:48).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 204-232), body EMA 30, use body on
    red bar and body > ema(body, 30) -> entry long;  green bar and body > ema(body, 30) -> entry short
    ((long and green bar) or (short and red bar)) and in profit vs avg price -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The final close_all acts on the position held at the bar's start and leaves the bar flat (C31-C39
      convention): a long in profit met by a green short signal ends that bar flat; without profit the
      short signal reverses. "In profit" compares the close with the fill price (the open after the
      entry signal). Repeated same-side signals are ignored (pyramiding 0).
    * The date inputs (1900 to 2100) are the author's window: dropped. REVERSAL INTENDED. FREQ = "1h"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colours, body size against its own average, profit sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored in original_sizing.txt.
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

NAME = "fmz_432354_noro_colorbar_fade"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_len": [30, 15],
    "use_body": [True, False],
}
DEFAULT_PARAMS = {"body_len": 30, "use_body": True}


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
    o, c = bars_df["open"], bars_df["close"]
    body = (c - o).abs()
    sb = body.ewm(span=int(p["body_len"]), adjust=False).mean()
    big = (body > sb).to_numpy() | (not bool(p["use_body"]))
    red, green = (c < o).to_numpy(), (c > o).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        start = pos
        ep = ov[e_i] if start != 0 else np.nan
        plus = (start == 1 and cv[i] > ep) or (start == -1 and cv[i] < ep)
        if red[i] and big[i] and start != 1:
            pos, e_i = 1, i + 1
        if green[i] and big[i] and start != -1:
            pos, e_i = -1, i + 1
        if ((start == 1 and green[i]) or (start == -1 and red[i])) and plus:
            pos = 0                                       # the final close_all leaves the bar flat
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
