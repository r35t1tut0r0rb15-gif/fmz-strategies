"""RSI average swing, broker days: the mean of six RSI(50)s (of ohlc4, close, open, high, hl2, hlc3)
crossing above 0.5 goes long, crossing below goes short; a long is also closed at 0.65 and a short at
0.35.
Port of FMZ strategy #427384 "RSI Average Reversion Trading Strategy".

FMZ source id: 427384

Source
    https://www.fmz.com/strategy/427384 (PineScript v5, FMZ last modified 2023-09-20 15:38:45).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 170-201), RSI 50, exits 0.65 / 0.35, both sides on
    avg = mean of rsi(x, 50) / 100 for x in ohlc4, close, open, high, hl2, hlc3
    long = avg > 0.5 and avg[1] < 0.5; short = avg < 0.5 and avg[1] > 0.5
    close long on avg >= 0.65 or short; close short on avg <= 0.35 or long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The opposite cross closes and re-enters on the same bar: REVERSAL INTENDED.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
    * FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427384_rsi_average_swing"
FAMILY = "rsi_oscillator"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_length": [50, 25],
    "long_exit": [0.65, 0.6],
    "short_exit": [0.35, 0.4],
}
DEFAULT_PARAMS = {"rsi_length": 50, "long_exit": 0.65, "short_exit": 0.35}


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
    ch = x.diff()
    up = _rma(ch.clip(lower=0), n).to_numpy()
    dn = _rma((-ch).clip(lower=0), n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        val = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, 100 - 100 / (1 + up / dn)))
    val[np.isnan(up) | np.isnan(dn)] = np.nan
    return val


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["rsi_length"])
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    srcs = [(o + h + lo + c) / 4, c, o, h, (h + lo) / 2, (h + lo + c) / 3]
    avg = sum(_rsi(s, n) for s in srcs) / 100 / 6
    a1 = np.concatenate(([np.nan], avg[:-1]))
    long_c, short_c = (avg > 0.5) & (a1 < 0.5), (avg < 0.5) & (a1 > 0.5)
    m = len(avg)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if long_c[i] and pos != 1:
            pos = 1
        elif short_c[i] and pos != -1:
            pos = -1
        elif pos == 1 and avg[i] >= p["long_exit"]:
            pos = 0
        elif pos == -1 and avg[i] <= p["short_exit"]:
            pos = 0
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
