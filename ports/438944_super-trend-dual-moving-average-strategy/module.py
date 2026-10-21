"""SuperTrend (10, 3) state on the side of the SMA 200, 1-hour bars: an up state above the SMA 200 holds a long, a down state below it holds a short (reversing); a down state above the SMA closes a long, an
up state below it closes a short; every trade has a 25 % stop from the fill.
Port of FMZ strategy #438944 "Super Trend Dual Moving Average Strategy" (ST Strategy).

FMZ source id: 438944

Source
    https://www.fmz.com/strategy/438944 (PineScript v5, FMZ last modified 2024-01-16 15:19:09).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 147-212), ATR 10 x 3; SMA 200; stop 25 %; pyramiding 1; 25 % of equity, commission 0.01 %
    upLevel / dnLevel = hl2 -/+ 3 atr, ratcheted;  trend = 1 if close > dnLevel[1], -1 if close < upLevel[1], else trend[1]
    trend 1 and close > sma 200 -> entry Long;  trend -1 and close < sma 200 -> entry Short;  trend -1 and close > sma -> close Long;  trend 1 and close < sma -> close Short;  exit(loss = 25 % of the average price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The states are levels, so the entries are sent on every bar of the state (pyramiding 1 holds one
      position). The stop is 25 % of the average price in ticks: sl_stop = 0.25 of the fill (sent from the
      first bar close inside the trade; the port starts it at the fill). strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The size, capital and commission
      are sizing / costs. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, ATR trend state and SMA side.
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

NAME = "fmz_438944_supertrend_state_sma200_stop"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.0, 2.0],
    "sl": [0.25, 0.10],
}
DEFAULT_PARAMS = {"factor": 3.0, "sl": 0.25, "atr_len": 10, "sma_len": 200}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    k = float(p["factor"])
    hl2 = (h + lo) / 2
    up_, dn_ = (hl2 - k * atr).to_numpy(), (hl2 + k * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    sma = c.rolling(int(p["sma_len"])).mean().to_numpy()
    m = len(cv)
    ul, dl = np.full(m, np.nan), np.full(m, np.nan)
    t = np.ones(m)
    for i in range(m):
        c1 = cv[i - 1] if i > 0 else np.nan
        u1 = ul[i - 1] if i > 0 else np.nan
        d1 = dl[i - 1] if i > 0 else np.nan
        ul[i] = max(up_[i], u1) if (c1 > u1 and not np.isnan(up_[i])) else up_[i]
        dl[i] = min(dn_[i], d1) if (c1 < d1 and not np.isnan(dn_[i])) else dn_[i]
        prev = t[i - 1] if i > 0 else 1.0
        t[i] = 1.0 if cv[i] > d1 else (-1.0 if cv[i] < u1 else prev)
    le = (t == 1) & (cv > sma)
    se = (t == -1) & (cv < sma)
    lx = (t == -1) & (cv > sma)
    sx = (t == 1) & (cv < sma)
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
