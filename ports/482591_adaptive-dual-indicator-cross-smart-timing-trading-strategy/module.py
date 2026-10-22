"""RSI 14 / CCI 20 extreme zones, hourly bars: a stay of three bars with RSI 14 at 31 or less and CCI at -120 or less buys, the first three bars with RSI 14 at 69 or more and CCI at 120 or more sell short; each trade is closed when RSI 30 moves 12 points in its favour or 8 against from its entry value, or CCI moves 100 against; reversing.
Port of FMZ strategy #482591 "Adaptive Dual Indicator Cross Smart Timing Trading Strategy" (RSI & CCI Strategy with Alerts).

FMZ source id: 482591

Source
    https://www.fmz.com/strategy/482591 (PineScript v6, FMZ last modified 2025-02-19 10:56:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-253), RSI 30 / RSI 14; CCI 20; zones 31 / -120 and 69 / 120; stay 2 bars (timeframe "60" default); exits RSI +12 / -8, CCI 100
    zone start bar t (reset when the zone ends);  buyOver = bar - t >= 2;  sellOver = bar - t <= 2
    buyOver and not isLongOpen -> entry Long (entryRSI := rsi30, entryCCI := cci);  sellOver and not isShortOpen -> entry Short
    isLongOpen and (rsi30 >= entryRSI + 12 or rsi30 <= entryRSI - 8 or cci <= entryCCI - 100) -> close Long;  mirror for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * On the hourly chart the timeframe switch takes its defaults: RSI 30 for the exits, CCI 20, a stay of
      2 bars. The long needs the zone held for at least 2 bars after it starts, the short only for at most
      2 bars after it starts (<= as written), so a short can be sent on the zone's first bar. The script's
      own isLongOpen / isShortOpen flags follow the orders (no other exit exists), so the port keeps them
      in a loop with the entry RSI / CCI values; the exit values are fixed at the entry bar. The CCI / RSI
      "buy / sell" plots and the commented-out block are display only. REVERSAL INTENDED. No sizing code.
      FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI / CCI extreme stays with exits relative to the entry readings.
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

NAME = "fmz_482591_rsi14_cci20_extreme_stay_entry_relative_exit_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cci_length": [20, 14],
    "rsi_exit_length": [30, 14],
}
DEFAULT_PARAMS = {"cci_length": 20, "rsi_exit_length": 30, "stay_over": 2}


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
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _cci(x, n):
    """Pine ta.cci: (x - sma) / (0.015 x mean absolute deviation); na when the deviation is 0."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        mu = w.mean(axis=1)
        dev = np.abs(w - mu[:, None]).mean(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            out[n - 1:] = np.where(dev > 0, (v[n - 1:] - mu) / (0.015 * dev), np.nan)
    return pd.Series(out, index=x.index)


def _zone_age(flag):
    """Bars since the current run of `flag` began (NaN outside a run), as the var start-bar trackers."""
    f = np.asarray(flag, dtype=bool)
    out = np.full(len(f), np.nan)
    start = -1
    for i in range(len(f)):
        if f[i]:
            if start < 0:
                start = i
            out[i] = i - start
        else:
            start = -1
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r14 = _rsi(c, 14)
    rx = _rsi(c, int(p["rsi_exit_length"])).to_numpy(dtype=float)
    cci = _cci(c, int(p["cci_length"]))
    st = int(p["stay_over"])
    age_b = _zone_age(((r14 <= 31) & (cci <= -120)).to_numpy())
    age_s = _zone_age(((r14 >= 69) & (cci >= 120)).to_numpy())
    bo = ~np.isnan(age_b) & (np.nan_to_num(age_b, nan=-1) >= st)
    so = ~np.isnan(age_s) & (np.nan_to_num(age_s, nan=99) <= st)
    cv = cci.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    side, er, ec = 0, np.nan, np.nan
    for i in range(m):
        if bo[i] and side != 1:
            le[i], side, er, ec = True, 1, rx[i], cv[i]
        if so[i] and side != -1:
            se[i], side, er, ec = True, -1, rx[i], cv[i]
        if side == 1 and not le[i] and (rx[i] >= er + 12 or rx[i] <= er - 8 or cv[i] <= ec - 100):
            lx[i], side = True, 0
        elif side == -1 and not se[i] and (rx[i] <= er - 12 or rx[i] >= er + 8 or cv[i] >= ec + 100):
            sx[i], side = True, 0
    idx = c.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
