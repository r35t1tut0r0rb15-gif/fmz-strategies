"""A "market sentiment" ratio (EMA 49 of the close change over EMA 49 of volume) put through a MACD (EMA 40 / 204, signal 20): the histogram crossing above 0 goes long, crossing under 0 closes; hourly bars, long only.
Port of FMZ strategy #431970 "Momentum Market Sentiment Indicator Strategy" (Sentiment Oscillator (dannylimardi)).

FMZ source id: 431970

Source
    https://www.fmz.com/strategy/431970 (PineScript v4, FMZ last modified 2023-11-13 17:51:20).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 177-222), sentiment lookback 49; fast EMA 40, slow EMA 204; signal 20
    marketSentiment = ema(close - close[1], 49) / ema(volume, 49) x 1e8;  macd = ema(ms, 40) - ema(ms, 204);  hist = macd - ema(macd, 20)
    crossover(hist, 0) -> entry Buy;  crossunder(hist, 0) -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 1e8 factor scales the ratio only; the crossings do not depend on it. The display switches only
      feed plots. Long only. The 100 % of equity and the commission are sizing and costs. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD of a price-change-per-volume ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 100, commission 0.08 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the sentiment ratio's denominator ema(volume, 49); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_431970_change_per_volume_sentiment_macd_hist_zero_long"
FAMILY = "volume_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_ema": [40, 20],
    "slow_ema": [204, 100],
}
DEFAULT_PARAMS = {"ms_len": 49, "fast_ema": 40, "slow_ema": 204, "signal_len": 20}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["ms_len"])
    ve = _ema(v, n)
    ms = _ema(c.diff(), n) / ve.where(ve != 0) * 1e8
    macd = _ema(ms, int(p["fast_ema"])) - _ema(ms, int(p["slow_ema"]))
    hist = macd - _ema(macd, int(p["signal_len"]))
    hp = hist.shift(1)
    up = ((hist > 0) & (hp <= 0)).to_numpy()
    dn = ((hist < 0) & (hp >= 0)).to_numpy()
    m = len(up)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and up[i]:
            le[i], pos = True, 1
        elif pos == 1 and dn[i]:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
