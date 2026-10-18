"""Parabolic SAR against the SMA 1000, 1-minute bars: below the SMA with the SAR under the close goes long; above the SMA with the SAR over the
close goes short (reversing). The "time-based exit" compares the bar time with a time five minutes AFTER the same bar, which is
never true, so there is no exit (as written).
Port of FMZ strategy #435704 "基于SMA和PSAR指标的多空策略SMA-and-PSAR-Strategy-for-Spot-Trading" (SMA and Parabolic SAR Strategy with Time-Based Exit).

FMZ source id: 435704

Source
    https://www.fmz.com/strategy/435704 (PineScript v4, FMZ last modified 2023-12-18 10:31:31).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 125-161), SAR 0.02 / 0.01 / 0.2; SMA 1000 (named sma100)
    isUpTrend = close < sma(close, 1000) (inverted, as written);  buyCondition = isUpTrend and sar < close;  sellCondition = not isUpTrend and sar > close
    buyCondition -> entry long;  sellCondition -> entry short;  exit(from_entry, when = time[0] > timestamp(year, month, dayofmonth, hour, minute + 5))

Interpretation choices (Pine rules in SURVEY_README.md)
    * "Up trend" is close UNDER the SMA, as written. The exit condition is time > (this bar's time +
      5 minutes), always false: strategy.exit with no stop or limit never fires. The port has no
      exit; the entries reverse: REVERSAL INTENDED (the intended five-minute exit is owed). The SAR is
      Pine's sar(start, increment, maximum), computed in the script's own way (starts at bar 1).
      FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: REVIEW, the time exit is never true: no exit as written.
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

NAME = "fmz_435704_sma_psar_reversal"
FAMILY = "trend_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [1000, 500],
    "psar_start": [0.02, 0.01],
}
DEFAULT_PARAMS = {"sma_len": 1000, "psar_start": 0.02, "psar_inc": 0.01, "psar_max": 0.2}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar(start, inc, max), as the reference implementation in the Pine manual."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    sar = pd.Series(_sar(h, lo, c, float(p["psar_start"]), float(p["psar_inc"]), float(p["psar_max"])), index=bars_df.index)
    close = bars_df["close"]
    sma = close.rolling(int(p["sma_len"])).mean()
    up = close < sma
    buy = (up & (sar < close)).fillna(False).astype(bool)
    sell = ((~up) & (sar > close) & sma.notna()).fillna(False).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
