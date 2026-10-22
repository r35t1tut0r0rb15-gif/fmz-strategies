"""Deep Bollinger breaks on calm bars, 1-minute bars, long only (trade direction 1): from flat, a bar without a 0.5 % body jump closing 25 % of the band width under the lower band goes long; the close
over the upper band plus 15 % of the width, or 5.5 % under the fill, closes.
Port of FMZ strategy #444009 "Bollinger Bands Breakout with Volatility Filter Strategy" ([Oppen Chow] Super BBS 1.0).

FMZ source id: 444009

Source
    https://www.fmz.com/strategy/444009 (PineScript v5, FMZ last modified 2024-03-08 15:28:05).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-202), BB 20 / 2; long breakout 25 %, short breakout 50 %; volatility 0.5 %; long settle -0.15, short settle 0.4; drawdown 5.5 %; trade direction 1; 100 % of equity, capital 500, commission 0.08; pyramiding 2
    flat and not (close - open) / open > 0.5 %: direction >= 0 and close < lower - area x 25 % -> entry Long;  direction <= 0 and close > upper + area x 50 % -> entry Short
    long and close > upper - area x (-0.15) -> close;  long and (avg - close) / avg >= 5.5 % -> close;  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * Trade direction 1 enables only the long branch. Entries need a flat position, so pyramiding 2
      never adds. The drawdown stop compares the close with the average (fill) price at the bar close.
      The volatility test reads only the current bar, as written. Pine's stdev is the population
      deviation. Long only. The percent-of-equity size, capital and commission are sizing and costs.
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, deep band breaks with a calm-bar filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
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

NAME = "fmz_444009_deep_bb_break_calm_bar_long_1m"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lower_breakout": [0.25, 0.5],
    "max_drawdown": [0.055, 0.03],
}
DEFAULT_PARAMS = {"lower_breakout": 0.25, "max_drawdown": 0.055, "volatility": 0.005, "long_win": -0.15}


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
    basis = c.rolling(20).mean()
    dev = 2 * c.rolling(20).std(ddof=0)
    up, dn = basis + dev, basis - dev
    area = up - dn
    calm = ~((c - o) / o > float(p["volatility"]))
    go = (calm & (c < dn - area * float(p["lower_breakout"]))).to_numpy()
    tp = (c > up - area * float(p["long_win"])).to_numpy()
    cv, ov = c.to_numpy(dtype=float), o.to_numpy(dtype=float)
    dd = float(p["max_drawdown"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, fill = False, np.nan
    for i in range(m):
        if go[i] and not held:
            le[i] = True
            if i + 1 < m:
                fill = ov[i + 1]
        elif held and (tp[i] or (fill - cv[i]) / fill >= dd):
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
