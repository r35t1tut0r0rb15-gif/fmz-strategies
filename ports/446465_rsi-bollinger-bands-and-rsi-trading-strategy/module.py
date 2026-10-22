"""Closes under the lower Bollinger band (20, 1) with the RSI 14 under 30, at least 5 bars after the previous buy signal, go long, 1-hour bars, long only; a close over the upper band with the RSI over 70
closes.
Port of FMZ strategy #446465 "布林带与RSI交易策略-Bollinger-Bands-and-RSI-Trading-Strategy" (cakes'Strategy For RSI).

FMZ source id: 446465

Source
    https://www.fmz.com/strategy/446465 (PineScript v4, FMZ last modified 2024-03-28 18:11:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-175), RSI 14 (rma form), levels 30 / 70; BB 20 / 1; buy interval 5 bars; 100 % of equity, capital 100000
    lastBuyBar starts at the first bar;  close < lower and rsi < 30 and bar_index - lastBuyBar >= 5 -> entry Long, lastBuyBar = bar_index;  close > upper and rsi > 70 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * lastBuyBar starts at the first bar and is moved by every buy signal, also one taken while long
      (the entry itself is then ignored: pyramiding 0). The rsi formula is the script's own (down == 0
      -> 100, up == 0 -> 0). Pine's stdev is the population deviation. Long only. The 100 % of equity
      size is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, lower-band RSI entries spaced by bars, upper-band RSI exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 100 % of equity size and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446465_lower_band_rsi_spaced_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "buy_interval": [5, 10],
    "rsi_lower": [30.0, 25.0],
}
DEFAULT_PARAMS = {"buy_interval": 5, "rsi_lower": 30.0, "rsi_upper": 70.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), 14), _rma((-d).clip(lower=0), 14)
    with np.errstate(divide="ignore", invalid="ignore"):
        base = 100 - 100 / (1 + up / dn)
    rsi = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, base))   # na stays na
    basis, sd = c.rolling(20).mean(), c.rolling(20).std(ddof=0)
    with np.errstate(invalid="ignore"):
        trig = (c < basis - sd).to_numpy() & (rsi < float(p["rsi_lower"]))
        out = (c > basis + sd).to_numpy() & (rsi > float(p["rsi_upper"]))
    m = len(trig)
    le = np.zeros(m, dtype=bool)
    last = 0                                         # lastBuyBar starts at the first bar
    k = int(p["buy_interval"])
    for i in range(m):
        if trig[i] and i - last >= k:
            le[i] = True
            last = i
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(out, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
