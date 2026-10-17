"""Noro's distance fades, 3-minute bars: when the gap between the last green close and the last red close exceeds twice its
30-bar average, a red bar with the fast RSI 7 under 30 goes long and a green bar with it over 70 goes short; the first
bar of the trade's own colour (green for a long, red for a short) closes it. The martingale lot is sizing.
Port of FMZ strategy #432183 "Trend Following Strategy Based on Distance with Trailing Stop Loss" (Noro's Distance Strategy v1.0).

FMZ source id: 432183

Source
    https://www.fmz.com/strategy/432183 (PineScript v2, FMZ last modified 2023-11-15 11:24:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 187-250), fast RSI 7, limit 30, distance average 30 x 2; martingale lot, pyramiding 10
    lastg = close of the last green bar, lastr = of the last red bar; dist = lastg - lastr; adist = sma(dist, 30)
    red bar and dist > 2 adist and rsi7 < 30 -> (close_all if short) entry long
    green bar and dist > 2 adist and rsi7 > 70 -> (close_all if long) entry short
    (long and green bar) or (short and red bar) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * dist is signed as written (lastg - lastr), so the rule fires only when the last green close sits
      well above the last red close. A green / red bar is close > open / close < open.
    * The final close_all acts on the position held at the bar's start and leaves the bar flat (C31-C39
      convention): a long met by a short signal (a green bar) and a short met by a long signal (a red
      bar) both end that bar flat, so the position never reverses in one bar. Repeated same-side
      signals are adds (pyramiding 10): criterion 4, not ported.
    * The martingale multiplier and the lot formula are sizing (quoted in original_sizing.txt); the
      date inputs (2018 to 2100) are the author's window: dropped. Opposite entries cannot occur.
      FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, close-to-close distance against its own average, RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, the capital % input and the martingale lot stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432183_noro_distance_fade"
FAMILY = "candle_pattern"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [7, 14],
    "dist_mult": [2.0, 1.5],
}
DEFAULT_PARAMS = {"rsi_len": 7, "rsi_limit": 30, "dist_len": 30, "dist_mult": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fast_rsi(c, n):
    d = c.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(~((up == 0) & (dn != 0)), 0.0)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    green, red = c > o, c < o
    cv, gv, rv = c.to_numpy(dtype=float), green.to_numpy(), red.to_numpy()
    lg, lr = np.full(len(cv), np.nan), np.full(len(cv), np.nan)
    g_, r_ = np.nan, np.nan
    for i in range(len(cv)):                            # the last green / red close up to this bar
        if gv[i]:
            g_ = cv[i]
        if rv[i]:
            r_ = cv[i]
        lg[i], lr[i] = g_, r_
    dist = pd.Series(lg - lr, index=c.index)
    adist = dist.rolling(int(p["dist_len"])).mean()
    big = dist > adist * float(p["dist_mult"])
    r = _fast_rsi(c, int(p["rsi_len"]))
    lim = float(p["rsi_limit"])
    up = (red & big & (r < lim)).to_numpy()
    dn = (green & big & (r > 100 - lim)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        start = pos
        if up[i]:
            pos = 1
        if dn[i]:
            pos = -1
        if (start == 1 and gv[i]) or (start == -1 and rv[i]):
            pos = 0                                       # the final close_all leaves the bar flat
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt != 1)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt != -1)
    return tuple(pd.Series(a, index=bars_df.index) for a in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
