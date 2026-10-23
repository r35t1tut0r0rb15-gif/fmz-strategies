"""Hourly bars, long only: an EMA 9 / 21 or MACD cross-up, an RSI 14 under 30 or a close under the lower Bollinger band (20, 2), on volume over 1.5 x its 20-bar average, goes long; the sell closes an entry id that is never opened, so the long is never closed (as written).
Port of FMZ strategy #488029 "Multi Indicator Dynamic Trading Strategy with Volume Confirmation System" (Advanced Trading Strategy (yunusrrkmz)).

FMZ source id: 488029

Source
    https://www.fmz.com/strategy/488029 (PineScript v6, FMZ last modified 2025-03-24 15:12:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 150-219), EMA 9 / 21; MACD 12 / 26 / 9; RSI 14 (30 / 70); BB 20 x 2; volume SMA 20 x 1.5
    buyCondition = (crossover(ema9, ema21) or crossover(macd, signal) or rsi < 30 or close < lowerBand) and volume > 1.5 x sma(volume, 20) -> entry Buy
    sellCondition = (the mirrors) and the volume test -> strategy.close("Sell")  (no entry is named "Sell")

Interpretation choices (Pine rules in SURVEY_README.md)
    * The only close names "Sell", which no entry uses, so it never acts: the first qualifying bar opens a
      long held to the end of the data (weird case; as #458234 for a script with no working exit). Long
      only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, any of four bullish triggers on high volume.
    3 crypto-exchange-only: no (exchange pair in the header only (BNB_USDT)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488029_any_bullish_trigger_volume_no_exit_1h_long_only"
FAMILY = "indicator_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_mult": [1.5, 2.0],
    "rsi_os": [30.0, 25.0],
}
DEFAULT_PARAMS = {"vol_mult": 1.5, "rsi_os": 30.0}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    f, s = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, 14)
    lower = c.rolling(20).mean() - 2.0 * c.rolling(20).std(ddof=0)
    trig = (((f > s) & (f.shift(1) <= s.shift(1))) | ((macd > sig) & (macd.shift(1) <= sig.shift(1)))
            | (r < float(p["rsi_os"])) | (c < lower))
    entry = trig & (v > v.rolling(20).mean() * float(p["vol_mult"]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
