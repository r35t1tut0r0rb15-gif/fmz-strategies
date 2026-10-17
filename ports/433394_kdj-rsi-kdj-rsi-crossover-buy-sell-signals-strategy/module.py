"""KDJ and RSI crosses, broker days: the J line crossing above K with RSI 6 above RSI 12, or with RSI 6 crossing above RSI
24, or RSI 6 crossing above RSI 24 below 40, goes long; the mirror conditions go short. Always in after the first signal.
Port of FMZ strategy #433394 "基于KDJ和RSI的买卖点策略KDJ-RSI-Crossover-Buy-Sell-Signals-Strategy" (buy/sell KDJ RSI).

FMZ source id: 433394

Source
    https://www.fmz.com/strategy/433394 (PineScript v5, FMZ last modified 2023-11-27 10:57:16).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 163-201), KDJ 9 / 3, RSI 6 / 12 / 24
    RSV = 100 (close - lowest(low, 9)) / (highest(high, 9) - lowest(low, 9));  K = bcwsma(RSV, 3, 1), D = bcwsma(K, 3, 1), J = 3K - 2D
    long = xover(J, K) and rsi6 > rsi12 or xover(J, K) and xover(rsi6, rsi24) or xover(rsi6, rsi24) and rsi6 < 40;  short mirrors (rsi6 > 60)

Interpretation choices (Pine rules in SURVEY_README.md)
    * bcwsma(s, 3, 1) = (s + 2 nz(prev)) / 3, starting from 0, as written. RSI is Wilder's.
    * A long and a short signal cannot fire on one bar (the crosses exclude each other).
      strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillator crosses and levels.
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

NAME = "fmz_433394_kdj_rsi_cross"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kdj_len": [9, 14],
    "rsi_fast": [6, 9],
}
DEFAULT_PARAMS = {"kdj_len": 9, "signal": 3, "rsi_fast": 6, "rsi_mid": 12, "rsi_slow": 24}


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


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())


def _bcwsma(s, ln, mw):
    v = s.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        out[i] = (mw * v[i] + (ln - mw) * (0.0 if np.isnan(prev) else prev)) / ln
        prev = out[i]
    return pd.Series(out, index=s.index)


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["kdj_len"])
    hh, ll = h.rolling(n).max(), lo.rolling(n).min()
    rsv = 100 * (c - ll) / (hh - ll)
    k = _bcwsma(rsv, int(p["signal"]), 1)
    d = _bcwsma(k, int(p["signal"]), 1)
    j = 3 * k - 2 * d
    r1, r2, r3 = _rsi(c, int(p["rsi_fast"])), _rsi(c, int(p["rsi_mid"])), _rsi(c, int(p["rsi_slow"]))
    lc = ((_xo(j, k) & (r1 > r2)) | (_xo(j, k) & _xo(r1, r3)) | (_xo(r1, r3) & (r1 < 40))).to_numpy()
    sc = ((_xo(k, j) & (r1 < r2)) | (_xo(k, j) & _xo(r3, r1)) | (_xo(r3, r1) & (r1 > 60))).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if lc[i]:
            pos = 1
        elif sc[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index)
                 for a in ((tgt == 1) & (prev != 1), false, (tgt == -1) & (prev != -1), false.copy()))


def portfolio_kwargs(**params):
    return {}
