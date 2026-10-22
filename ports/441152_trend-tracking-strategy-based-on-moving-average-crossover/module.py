"""EMA crossings with a strong smoothed RSI, 2-hour bars, long only: the EMA 9 crossing over the EMA 21, or the EMA 21 over the EMA 51, with the RSI 14 of the SMA 14 above 65 goes long; the EMA 9
crossing under the EMA 51, the RSI under 40, or the close 25 % above / 2 % under the fill closes.
Port of FMZ strategy #441152 "Trend Tracking Strategy Based on Moving Average Crossover" (new).

FMZ source id: 441152

Source
    https://www.fmz.com/strategy/441152 (PineScript v5, FMZ last modified 2024-02-06 11:37:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-164), EMA 9 / 21 / 51 / 100 (200 unused); rsi2 = rsi(sma(close, 14), 14); qty 1; start / end timestamps (unused)
    LongEntry = (crossover(ema9, ema21) or crossover(ema21, ema51)) and rsi2 > 65;  LongEntry and rsi2 > 60 -> entry Long qty 1
    LongExit = crossunder(ema9, ema51) or close > position_avg_price 1.25 or rsi2 < 40 or close < position_avg_price 0.98 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The price exits are bar-close tests of the close against the fill price (the average price is na
      while flat), sent at the next open. A close acts only on the held position. The timestamps are never
      used. Long only. The qty of 1 is sizing. FREQ = "2h" from the backtest header (bars on UTC multiples
      of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings, smoothed RSI and close-vs-fill tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG441152 (2 members, best partner #443251, Jaccard 0.918); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441152_ema_cross_strong_smoothed_rsi_long"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_entry": [65, 55],
    "rsi_exit": [40, 30],
}
DEFAULT_PARAMS = {"rsi_entry": 65, "rsi_exit": 40, "up_mult": 1.25, "down_mult": 0.98}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e0, e1, e2 = (c.ewm(span=n, adjust=False).mean() for n in (9, 21, 51))
    r2 = _rsi(c.rolling(14).mean(), 14)
    xo01 = (e0 > e1) & (e0.shift(1) <= e1.shift(1))
    xo12 = (e1 > e2) & (e1.shift(1) <= e2.shift(1))
    re = float(p["rsi_entry"])
    go = ((xo01 | xo12) & (r2 > re) & (r2 > 60)).to_numpy()
    xa = (((e0 < e2) & (e0.shift(1) >= e2.shift(1))) | (r2 < float(p["rsi_exit"]))).to_numpy()
    cv = c.to_numpy(dtype=float)
    ov = bars_df["open"].to_numpy(dtype=float)
    um, dm = float(p["up_mult"]), float(p["down_mult"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, entry_i = 0, -1
    for i in range(m):
        if held == 1 and i >= entry_i:
            fill = ov[entry_i]
            if xa[i] or cv[i] > fill * um or cv[i] < fill * dm:
                lx[i], held = True, 0
                continue
        if held == 0 and go[i] and i + 1 < m:
            le[i], held, entry_i = True, 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
