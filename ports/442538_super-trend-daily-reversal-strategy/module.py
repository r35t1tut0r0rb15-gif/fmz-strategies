"""SuperTrend(3, 1.3) flips filtered by a moving rate of change, 1-hour bars: a flip up with the EMA 15 of the 30-bar ROC beyond +-3 % goes long, a flip down short; a 6 % stop from the fill; reversing.
Port of FMZ strategy #442538 "Super Trend Daily Reversal Strategy" (Super Trend Daily BF).

FMZ source id: 442538

Source
    https://www.fmz.com/strategy/442538 (PineScript v4, FMZ last modified 2024-02-22 16:22:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 155-261), SuperTrend ATR 3 x 1.3; ROC 30, change 6 %; stop type Fixed 6 % (ATR-derived option 20 x 1.5 off); 100 % of equity, capital 10000, commission 0.075; dates dropped
    dir flips: dir == -1 and close > shortStopPrev -> 1;  dir == 1 and close < longStopPrev -> -1;  isMoving = ema(roc(30), 15) > 3 or < -3
    long = dir flips up and isMoving -> entry L;  short = dir flips down and isMoving -> entry S
    exit L (stop = avg (1 - 6 %), when bars since the last open long signal > 0 and in a long signal);  exit S mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stops are sent from the bar after the signal at the average (fill) price, so they are fixed
      fractions 0.06 of the fill, active from the fill bar (#440797). The in-signal state matches the
      held side whenever a position is open. A repeat flip in the held direction is refused (default
      pyramiding) and after a stop-out it re-enters. The ATR-derived stop option is off. strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The percent-of-equity
      size, capital and commission are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed from the fill.
    2 generic: PASS, SuperTrend flips with a rate-of-change filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_442538_supertrend_flip_roc_filter_pct_stop"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [1.3, 3.0],
    "sl_pct": [0.06, 0.03],
}
DEFAULT_PARAMS = {"mult": 1.3, "sl_pct": 0.06, "length": 3, "roc_length": 30, "pcnt_change": 6.0}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _dir(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = (float(p["mult"]) * _rma(tr, int(p["length"]))).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    out = np.ones(m, dtype=np.int8)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        ls, ss = hl2[i] - atr[i], hl2[i] + atr[i]
        lsp = ls if np.isnan(ls_p) else ls_p
        ssp = ss if np.isnan(ss_p) else ss_p
        if i > 0 and cv[i - 1] > lsp:
            ls = max(ls, lsp)
        if i > 0 and cv[i - 1] < ssp:
            ss = min(ss, ssp)
        if d == -1 and cv[i] > ssp:
            d = 1
        elif d == 1 and cv[i] < lsp:
            d = -1
        out[i] = d
        ls_p, ss_p = ls, ss
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = _dir(bars_df, p)
    d1 = np.concatenate(([1], d[:-1]))
    rl = int(p["roc_length"])
    roc = 100 * (c - c.shift(rl)) / c.shift(rl)
    er = roc.ewm(span=rl // 2, adjust=False).mean()
    half = float(p["pcnt_change"]) / 2
    moving = ((er > half) | (er < -half)).to_numpy()
    lsig = (d == 1) & (d1 == -1) & moving
    ssig = (d == -1) & (d1 == 1) & moving
    s_ = float(p["sl_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        if i + 1 < m:
            if lsig[i] and pos != 1:
                le[i], pos, entry_i = True, 1, i + 1
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
