"""Counter-candle reversals with a regression-slope filter, 30-minute bars: an up candle closes a long and, with the 14-bar regression slope of hlc3 at or under zero, goes short; a down candle closes a short and,
with the slope at or above zero, goes long.
Port of FMZ strategy #437045 "Reverse Linear Regression Strategy" (Reverse Up/Down Strategy).

FMZ source id: 437045

Source
    https://www.fmz.com/strategy/437045 (PineScript v4, FMZ last modified 2023-12-29 17:15:07).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 129-169), bars up 1, bars down 1, slope length 14 (ATR channel plotted only); pyramiding 2
    lrs = linreg(hlc3, 14, 0) - linreg(hlc3, 14, 1) (the regression slope);  ups / dns = runs of up / down candles
    open < close -> close buy, and if ups >= 1 and lrs <= 0 -> entry sell;  open > close -> close sell, and if dns >= 1 and lrs >= 0 -> entry buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * linreg(src, n, 0) - linreg(src, n, 1) is the least-squares slope of the window. The second entry that
      pyramiding 2 allows is an add (sizing): the port holds one position. The ATR channel is plotted only.
      Orders follow the script's call order (the close, then the entry). REVERSAL INTENDED. The 100 % of
      equity size is sizing. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candle colour and regression slope sign.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 2 and the percent-of-equity size stored.
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

NAME = "fmz_437045_counter_candle_linreg_slope"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slope_len": [14, 28],
    "bars_run": [1, 2],
}
DEFAULT_PARAMS = {"slope_len": 14, "bars_run": 1}


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


def _slope(y, n):
    """Least-squares slope over the last n values (x = 0 oldest .. n - 1 newest)."""
    sx = n * (n - 1) / 2
    sxx = (n - 1) * n * (2 * n - 1) / 6
    sxy = sum((n - 1 - k) * y.shift(k) for k in range(n))
    sy = y.rolling(n).sum()
    return (n * sxy - sx * sy) / (n * sxx - sx * sx)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    lrs = _slope((h + lo + c) / 3, int(p["slope_len"])).to_numpy()
    green, red = (o < c).to_numpy(), (o > c).to_numpy()
    k = int(p["bars_run"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ups = dns = 0
    pos = 0
    with np.errstate(invalid="ignore"):
        for i in range(m):
            ups = ups + 1 if green[i] else 0
            dns = dns + 1 if red[i] else 0
            new = pos
            if green[i]:
                if pos == 1:
                    new = 0
                if ups >= k and lrs[i] <= 0:
                    new = -1
            if red[i]:
                if pos == -1:
                    new = 0
                if dns >= k and lrs[i] >= 0:
                    new = 1
            if new == 1 and pos != 1:
                le[i] = True
            elif new == -1 and pos != -1:
                se[i] = True
            elif new == 0 and pos == 1:
                lx[i] = True
            elif new == 0 and pos == -1:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
