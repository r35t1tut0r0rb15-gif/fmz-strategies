"""Durenard's adaptive moving-average channel, broker days: an AMA whose speed adapts to a signal-to-noise ratio carries a
channel scaled by the recent up / down moves (beta 2.1); a close above the channel goes long, below it goes short.
Port of FMZ strategy #430855 "Adaptive Moving Average Channel Breakout Strategy" ([CS] AMA Strategy - Channel Break Out).

FMZ source id: 430855

Source
    https://www.fmz.com/strategy/430855 (PineScript v4, FMZ last modified 2023-11-02 15:05:56).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 195-307), SNR factor 2.1, sensitivity look-back 5, beta 2.1
    ama = alpha[1] price + (1 - alpha[1]) ama[1]
    dev_max = alpha[1] max(ret, 0) + (1 - alpha[1]) dev_max[1]; dev_min = -alpha[1] min(ret, 0) + (1 - alpha[1]) dev_min[1]
    hb = (1 + beta dev_max[1]) ama; lb = (1 - beta dev_min[1]) ama
    snr = price > hb ? ((price - ama[1]) / ama[1]) / (beta dev_min) : price < lb ? -((price - ama[1]) / ama[1]) / (beta dev_max) : 0
    alpha = nwma((atan(2.1 snr) + pi/2) / pi, 5)
    price > hb -> entry long;  price < lb -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The recursion is transcribed bar by bar with nz() on the lagged terms. The zero-lag nwma uses
      Pine v4 integer division as written: fast = 5 / 2 = 2, lambda = 5 / 2 = 2, alpha = 2 x 4 / 3
      = 2, so nwma = 3 wma(x, 5) - 2 wma(wma(x, 5), 2). The AMA starts from 0 through nz() once alpha
      exists, as written.
    * testPeriod() is always true. strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, returns, an adaptive average and ratios.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_430855_durenard_ama_channel"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "beta": [2.1, 1.5],
    "snr_factor": [2.1, 1.2],
}
DEFAULT_PARAMS = {"beta": 2.1, "snr_factor": 2.1, "lookback": 5}


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


def _nz(v):
    return 0.0 if np.isnan(v) else v


def _wma_last(vals):
    n = len(vals)
    w = np.arange(1, n + 1, dtype=float)
    return float(np.dot(vals, w) / w.sum())


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    price = bars_df["close"].to_numpy(dtype=float)
    beta, snrf, lbk = float(p["beta"]), float(p["snr_factor"]), int(p["lookback"])
    fast = lbk // 2
    lam = lbk // fast
    a_nw = (lam * (lbk - 1)) // (lbk - lam)
    pi2 = np.pi / 2
    m = len(price)
    ama = np.full(m, np.nan)
    dmax, dmin = np.full(m, np.nan), np.full(m, np.nan)
    nat = np.full(m, np.nan)
    w5 = np.full(m, np.nan)
    alpha = np.full(m, np.nan)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        a1 = alpha[i - 1] if i > 0 else np.nan
        ama[i] = a1 * price[i] + (1 - a1) * (_nz(ama[i - 1]) if i > 0 else 0.0)
        ret = (price[i] - price[i - 1]) / price[i - 1] if i > 0 else np.nan
        dmax[i] = a1 * max(ret, 0.0) + (1 - a1) * (_nz(dmax[i - 1]) if i > 0 else 0.0) if not np.isnan(ret) else np.nan
        dmin[i] = -a1 * min(ret, 0.0) + (1 - a1) * (_nz(dmin[i - 1]) if i > 0 else 0.0) if not np.isnan(ret) else np.nan
        bhb1 = beta * dmax[i - 1] if i > 0 else np.nan
        blb1 = beta * dmin[i - 1] if i > 0 else np.nan
        hb = (1 + bhb1) * ama[i]
        lb = (1 - blb1) * ama[i]
        ama1 = ama[i - 1] if i > 0 else np.nan
        if price[i] > hb:
            snr = ((price[i] - ama1) / ama1) / (beta * dmin[i])
        elif price[i] < lb:
            snr = -((price[i] - ama1) / ama1) / (beta * dmax[i])
        else:
            snr = 0.0
        nat[i] = (np.arctan(snrf * snr) + pi2) / (2 * pi2)
        if i >= lbk - 1:
            w5[i] = _wma_last(nat[i - lbk + 1:i + 1])
        if i >= lbk and fast >= 1:
            w2 = _wma_last(w5[i - fast + 1:i + 1])
            alpha[i] = (1 + a_nw) * w5[i] - a_nw * w2
        if price[i] > hb:
            pos = 1
        elif price[i] < lb:
            pos = -1
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
