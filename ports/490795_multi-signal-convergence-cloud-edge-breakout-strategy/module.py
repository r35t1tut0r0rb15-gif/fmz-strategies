"""Ichimoku eight-signal vote, always in, broker days: when all eight bullish Ichimoku signals agree the strategy is
long; when none does it is short.
Port of FMZ strategy #490795 "多重信号一致性云层边缘突破策略-Multi-Signal-Convergence-Cloud-Edge-Breakout-Strategy" (CloudEdge).

FMZ source id: 490795

Source
    https://www.fmz.com/strategy/490795 (PineScript v6, FMZ last modified 2025-04-16 15:24:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 196-262), Ichimoku 9 / 26 / 52, displacement 26, thresholds 8 / 0
    s1 close > close[26]; s2 close > tenkan; s3 tenkan > kijun; s4-s8 = barssince(cross up) < barssince(cross down) of
    chikou / tenkan, chikou / kijun, tenkan / kijun, chikou / kumo (upper up, lower down), senkouA / senkouB
    (chikou = close[26]; kumo = max / min of senkouA[26], senkouB[26])
    count >= 8 -> entry long (close "Short");  else count <= 0 -> entry short (close "Long")

Interpretation choices (Pine rules in SURVEY_README.md)
    * Every series uses past bars only (chikou = close[26], the kumo shifted 26). barssince is na until the cross
      has happened once; a comparison with na is false, as in Pine.
    * The closes fall on the reversing entries' bars: a stop-and-reverse (REVERSAL INTENDED).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku comparisons.
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

NAME = "fmz_490795_ichimoku_eight_signal_vote"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bull_threshold": [8, 7],
    "bear_threshold": [0, 1],
}
DEFAULT_PARAMS = {"tenkan": 9, "kijun": 26, "senkou_b": 52, "displacement": 26, "bull_threshold": 8,
                  "bear_threshold": 0}


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


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _cross(a, b, up):
    return ((a > b) & (a.shift(1) <= b.shift(1))) if up else ((a < b) & (a.shift(1) >= b.shift(1)))


def _sooner(up, dn):
    """barssince(up) < barssince(dn); False when either is na."""
    bu, bd = _barssince(up.to_numpy(dtype=bool)), _barssince(dn.to_numpy(dtype=bool))
    with np.errstate(invalid="ignore"):
        return np.where(np.isnan(bu) | np.isnan(bd), False, bu < bd)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    mid = lambda n: (h.rolling(n).max() + lo.rolling(n).min()) / 2  # noqa: E731
    d = int(p["displacement"])
    tenkan, kijun = mid(int(p["tenkan"])), mid(int(p["kijun"]))
    sa, sb = (tenkan + kijun) / 2, mid(int(p["senkou_b"]))
    chikou = c.shift(d)
    k_up = np.maximum(sa.shift(d), sb.shift(d))
    k_lo = np.minimum(sa.shift(d), sb.shift(d))
    s = [(c > c.shift(d)).to_numpy(), (c > tenkan).to_numpy(), (tenkan > kijun).to_numpy(),
         _sooner(_cross(chikou, tenkan, True), _cross(chikou, tenkan, False)),
         _sooner(_cross(chikou, kijun, True), _cross(chikou, kijun, False)),
         _sooner(_cross(tenkan, kijun, True), _cross(tenkan, kijun, False)),
         _sooner(_cross(chikou, k_up, True), _cross(chikou, k_lo, False)),
         _sooner(_cross(sa, sb, True), _cross(sa, sb, False))]
    count = np.sum(np.vstack([np.asarray(x, dtype=bool) for x in s]), axis=0)
    long_c = count >= p["bull_threshold"]
    short_c = (~long_c) & (count <= p["bear_threshold"])
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(long_c, index=idx), false, pd.Series(short_c, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
