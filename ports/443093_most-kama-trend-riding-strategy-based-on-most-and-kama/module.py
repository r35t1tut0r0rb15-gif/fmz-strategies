"""MOST (a 3.3 % trailing band around a KAMA 3), daily bars, long only: the KAMA crossing over its MOST line goes long, crossing under closes.
Port of FMZ strategy #443093 "基于MOST和KAMA的趋势跟踪策略Trend-Riding-Strategy-Based-on-MOST-and-KAMA" (Atlantean Trend Signal BUY SELL Strategy).

FMZ source id: 443093

Source
    https://www.fmz.com/strategy/443093 (PineScript v5, FMZ last modified 2024-02-29 11:04:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 123-248), MA type KAMA, length 3; stop percent 3.3; screener modes off
    KAMA: nAMA = nz(nAMA[1]) + nsmooth (src - nz(nAMA[1])), fast 0.666, slow 0.0645;  longStop = kama (1 - 3.3 %) ratcheted, shortStop = kama (1 + 3.3 %) ratcheted;  dir flips on the previous stops
    MOST = dir == 1 ? longStop : shortStop;  crossover(kama, MOST) -> entry LONG;  crossunder(kama, MOST) -> close LONG

Interpretation choices (Pine rules in SURVEY_README.md)
    * The KAMA starts from 0 (nz) as written and converges; the MOST band follows the SuperTrend-style
      ratchet and direction flip on the KAMA. The other MA types are unused. Long only. No sizing code.
      FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, KAMA vs MOST band crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_443093_most_kama3_band_cross_long"
FAMILY = "adaptive_average"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_length": [3, 10],
    "percent": [3.3, 6.0],
}
DEFAULT_PARAMS = {"ma_length": 3, "percent": 3.3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _kama(c, n):
    noise = (c - c.shift(1)).abs().rolling(n).sum().to_numpy()
    sig = (c - c.shift(n)).abs().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    out = np.full(m, np.nan)
    prev = 0.0
    for i in range(m):
        if np.isnan(sig[i]) or np.isnan(noise[i]):
            out[i] = np.nan
            continue
        er = sig[i] / noise[i] if noise[i] != 0 else 0.0
        sm = (er * (0.666 - 0.0645) + 0.0645) ** 2
        prev = prev + sm * (cv[i] - prev)
        out[i] = prev
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ex = _kama(c, int(p["ma_length"]))
    f = float(p["percent"]) * 0.01
    m = len(ex)
    most = np.full(m, np.nan)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        if np.isnan(ex[i]):
            continue
        ls, ss = ex[i] * (1 - f), ex[i] * (1 + f)
        lsp = ls if np.isnan(ls_p) else ls_p
        ssp = ss if np.isnan(ss_p) else ss_p
        if ex[i] > lsp:
            ls = max(ls, lsp)
        if ex[i] < ssp:
            ss = min(ss, ssp)
        if d == -1 and ex[i] > ssp:
            d = 1
        elif d == 1 and ex[i] < lsp:
            d = -1
        most[i] = ls if d == 1 else ss
        ls_p, ss_p = ls, ss
    e = pd.Series(ex, index=c.index)
    mo = pd.Series(most, index=c.index)
    le = (e > mo) & (e.shift(1) <= mo.shift(1))
    lx = (e < mo) & (e.shift(1) >= mo.shift(1))
    false = pd.Series(False, index=c.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
