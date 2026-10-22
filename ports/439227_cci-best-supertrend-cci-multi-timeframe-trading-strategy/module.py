"""CCI(28) side of zero, 10-minute bars: a CCI above zero holds a long, below zero a short, an exact zero keeps the last side; reversing at each flip.
Port of FMZ strategy #439227 "基于超级趋势和CCI指标的多时间框架交易策略Best-Supertrend-CCI-Multi-Timeframe-Trading-Strategy" (Best Supertrend CCI Strategy).

FMZ source id: 439227

Source
    https://www.fmz.com/strategy/439227 (PineScript v4, FMZ last modified 2024-01-18 15:09:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 268-353), source close; CCI 28; mid line 0; [ST] factor 3, PD 3
    Trend = cci > 0 ? 1 : cci < 0 ? -1 : nz(Trend[1], 1);  Tsl = Trend == 1 ? TrendUp : TrendDown (plot only)
    entry Long when Trend == 1;  close Long when it flips to -1;  entry Short when Trend == -1;  close Short when it flips to 1

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trading side is the CCI's side of the mid line; the supertrend lines (TrendUp / TrendDown with
      ATR 3) only feed the plotted Tsl. While the CCI is not yet defined the comparisons are false and
      the side is the default 1, so the port holds a long from the first bar, as written. On a flip the
      close and the opposite entry come together and the reversal stands (as #438020). strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI side of a mid line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_439227_cci_side_of_midline_flip"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_period": [28, 14],
    "ml": [0.0, 50.0],
}
DEFAULT_PARAMS = {"cci_period": 28, "ml": 0.0}


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
    c = bars_df["close"]
    n = int(p["cci_period"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = ((c - ma) / (0.015 * dev)).to_numpy()
    ml = float(p["ml"])
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    t = 1
    for i in range(m):
        if cci[i] > ml:
            t = 1
        elif cci[i] < ml:
            t = -1
        tgt[i] = t
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
