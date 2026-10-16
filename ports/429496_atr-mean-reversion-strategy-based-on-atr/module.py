"""ATR divergence with a drift confirmation, long only, broker days: once the fast and slow ATR differ significantly
(a two-tailed z-test) and the log-return drift turns up, go long; the long is protected by a ratcheting
2 ATR trailing stop.
Port of FMZ strategy #429496 "基于ATR的均值回复策略Mean-Reversion-Strategy-Based-on-ATR" (Mean Reversion (ATR) Strategy v2 [KL]).

FMZ source id: 429496

Source
    https://www.fmz.com/strategy/429496 (PineScript v5, FMZ last modified 2023-10-17 16:27:44).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 162-237), ATR 14 vs 28, z 1.645, drift 14, trailing stop low - 2 x ATR(14)
    reject_H0 = |atr14 - atr28| / (stdev(tr,14) / sqrt(14)) > 1.645; latch = reject_H0 seen since the last position change
    drift = sma(log(close / close[1]), 14) - stdev(.., 14)^2 / 2; latch and drift > drift[1] -> entry long (pyramiding 1)
    while long: stop = max(stop, low - 2 x atr(14)), re-issued when it changes

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trail is ported natively (mark trailing_stop): {"type": "volatility", "atr_n": 14, "k": 2.0,
      "anchor": "high_low"}. Stated approximation: the source ratchets the bar LOW minus 2 ATR, the house
      the best HIGH minus 2 ATR (higher by up to a bar's range, so it exits earlier), on minutes.
    * The latch resets on every change of position; the port cannot see the trail's exits in simulate(),
      so it resets the latch on the bar after each entry signal (stated approximation). With
      pyramiding 1 a signal while long adds nothing.
    * Long only; Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). Stops on
      1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, ATR ratios, log returns and an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 1 stored; the trailing stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_429496_atr_divergence_drift_long"
FAMILY = "volatility_spike_reversal"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "z": [1.645, 1.96],
    "trail_k": [2.0, 3.0],
}
DEFAULT_PARAMS = {"len_fast": 14, "len_slow": 28, "z": 1.645, "len_drift": 14, "trail_atr": 14, "trail_k": 2.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    nf = int(p["len_fast"])
    se_ = tr.rolling(nf).std(ddof=0) / np.sqrt(nf)
    stat = (_rma(tr, nf) - _rma(tr, int(p["len_slow"]))) / se_.replace(0.0, np.nan)
    reject = (stat.abs() > p["z"]).to_numpy()
    lr = np.log(c / c.shift(1))
    nd = int(p["len_drift"])
    drift = lr.rolling(nd).mean() - lr.rolling(nd).std(ddof=0) ** 2 * 0.5
    up = (drift > drift.shift(1)).to_numpy()
    m = len(c)
    le = np.zeros(m, dtype=bool)
    latch = False
    reset_next = False
    for i in range(m):
        if reset_next:
            latch, reset_next = False, False
        if not latch:
            latch = bool(reject[i])
        if latch and up[i]:
            le[i], reset_next = True, True
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["trail_atr"]), "k": float(p["trail_k"]),
                      "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
