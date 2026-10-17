"""Daily Heikin Ashi close averages crossed on hourly bars, long only: the last completed broker day's Heikin Ashi close,
carried on the 1-hour bars, is smoothed by an EDSMA 30 (fast) and a 50-bar regression line (slow); the fast crossing
above the slow goes long, crossing below closes it.
Port of FMZ strategy #432357 "多时间框架MA蒙德里安交叉策略MZ-MA-Cross-Multiple-TimeFrame-Strategy" (MA MTF Cross Strategy (MZ MA Cross)).

FMZ source id: 432357

Source
    https://www.fmz.com/strategy/432357 (PineScript v4, FMZ last modified 2023-11-16 17:28:43).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 199-421), daily HA close, slow LRC 50, fast EDSMA 30 (super smoother 20, 2 poles), 3rd MA off
    x = security(heikinashi(tickerid), 'D', close)
    slow = linreg(x, 50, 0);  fast = edsma(x, 30): ssf of (x - x[2]) averaged, scaled by its stdev, alpha = 5 |scaled| / 30
    crossover(fast, slow) -> entry long;  crossunder(fast, slow) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(..., 'D') without lookahead is read as the last completed daily bar (SURVEY_README:
      higher timeframes from completed higher bars), built from the port's own bars on broker days
      (17:00 America/New_York): the daily Heikin Ashi candle (close = ohlc4, open = the average of the
      previous HA open and close). The averages then run on the hourly bars of that stepped series,
      as written (the MA functions are applied on the chart's bars).
    * EDSMA: zeros = x - nz(x[2]), averaged over two bars, a 2-pole super smoother (length 20) with
      nz on its own history, divided by its population stdev over 30 bars (0 when that is 0); alpha
      = 5 x |scaled| / 30; edsma = alpha x + (1 - alpha) nz(edsma[1]). The uptrend MA (off) and the
      other MA types are input options.
    * window() is always true. Long only; Opposite entries cannot occur. FREQ = "1h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, MA crosses of a daily Heikin Ashi close.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed quantity 5 and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily values on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432357_daily_ha_edsma_lrc_cross"
FAMILY = "multi_timeframe_ma"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast_len": [30, 15],
    "slow_len": [50, 100],
}
DEFAULT_PARAMS = {"fast_len": 30, "slow_len": 50, "ssf_len": 20}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _daily_ha_close(bars_df):
    """Heikin Ashi close of the last completed broker day, on every bar of the next one."""
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("open", "high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    ha_c = (d["open"] + d["high"] + d["low"] + d["close"]) / 4
    return pd.Series(ha_c.shift(1).reindex(day).to_numpy(), index=bars_df.index)


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line through the last n values, read at the last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        t = np.arange(n, dtype=float) - (n - 1) / 2.0
        slope = win @ t / float(t @ t)
        out[n - 1:] = win.mean(axis=1) + slope * (n - 1) / 2.0
    return pd.Series(out, index=x.index)


def _nz(v):
    return 0.0 if np.isnan(v) else v


def _edsma(x, n, ssf_len):
    v = x.to_numpy(dtype=float)
    m = len(v)
    zeros = np.array([v[i] - (_nz(v[i - 2]) if i >= 2 else 0.0) for i in range(m)])
    avz = np.concatenate(([np.nan], (zeros[1:] + zeros[:-1]) / 2))
    arg = np.sqrt(2) * np.pi / ssf_len
    a1 = np.exp(-arg)
    c2 = 2 * a1 * np.cos(arg)
    c3 = -a1 ** 2
    c1 = 1 - c2 - c3
    ssf = np.full(m, np.nan)
    for i in range(m):
        s1 = _nz(ssf[i - 1]) if i >= 1 else 0.0
        s2 = _nz(ssf[i - 2]) if i >= 2 else 0.0
        ssf[i] = c1 * avz[i] + c2 * s1 + c3 * s2
    sd = pd.Series(ssf).rolling(n).std(ddof=0).to_numpy()
    out = np.full(m, np.nan)
    for i in range(m):
        scaled = 0.0 if (np.isnan(sd[i]) or sd[i] == 0) else ssf[i] / sd[i]
        if np.isnan(sd[i]):
            scaled = np.nan
        alpha = 5 * abs(scaled) / n
        prev = _nz(out[i - 1]) if i >= 1 else 0.0
        out[i] = alpha * v[i] + (1 - alpha) * prev
    return pd.Series(out, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    x = _daily_ha_close(bars_df)
    slow = _linreg(x, int(p["slow_len"]))
    fast = _edsma(x, int(p["fast_len"]), int(p["ssf_len"]))
    le = ((fast > slow) & (fast.shift(1) <= slow.shift(1))).astype(bool)
    lx = ((fast < slow) & (fast.shift(1) >= slow.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
