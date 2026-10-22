"""CCI 10 crossings of zero (either way, as written) after an RSI 14 extreme within 4 bars with an RSI turn, 3-day bars: oversold with an RSI hook up and the close under the EMA 100 goes long; overbought with a hook down and the close over it goes short; reversing.
Port of FMZ strategy #489324 "EMA辅助极点反转交易策略-EMA-Assisted-Extreme-Point-Reversal-Trading-Strategy" (Extreme Points + 100 EMA Strategy).

FMZ source id: 489324

Source
    https://www.fmz.com/strategy/489324 (PineScript v5, FMZ last modified 2025-04-03 14:50:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 172-227), CCI 10; RSI 14 / 65 / 35; divergence (on); EMA 100
    ta.cross(cci, 0) and rsi <= 35 within 4 bars and rsi > rsi[1] < rsi[2] and close < ema100 -> entry Buy
    ta.cross(0, cci) and rsi >= 65 within 4 bars and rsi < rsi[1] > rsi[2] and close > ema100 -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross is true for a crossing in either direction, so both sides use any zero crossing of the CCI,
      as written. No exits: the opposite entry reverses (REVERSAL INTENDED). No sizing code. Bars are blocks
      of three broker days (17:00 America/New_York) counted from 1970-01-01, stamped with their first
      minute. FREQ = "3D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, CCI zero crossings after RSI extremes with an EMA filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: three-broker-day blocks (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489324_cci10_zero_cross_rsi_extreme_hook_ema100_reversal"
FAMILY = "cci"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (three broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ccimomLength": [10, 20],
    "rsiOversold": [35, 25],
}
DEFAULT_PARAMS = {"ccimomLength": 10, "rsiOversold": 35, "rsiLength": 14, "emaLength": 100, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["ccimomLength"])
    ma = c.rolling(n).mean()
    md = c.rolling(n).apply(lambda a: np.abs(a - a.mean()).mean(), raw=True)
    cci = (c - ma) / (0.015 * md.where(md > 0))
    crossed = ((cci > 0) & (cci.shift(1) <= 0)) | ((cci < 0) & (cci.shift(1) >= 0))
    r = _rsi(c, int(p["rsiLength"]))
    os_ = float(p["rsiOversold"])
    ob = 100 - os_
    was_os = (r <= os_) | (r.shift(1) <= os_) | (r.shift(2) <= os_) | (r.shift(3) <= os_)
    was_ob = (r >= ob) | (r.shift(1) >= ob) | (r.shift(2) >= ob) | (r.shift(3) >= ob)
    hook_up = (r > r.shift(1)) & (r.shift(1) < r.shift(2))
    hook_dn = (r < r.shift(1)) & (r.shift(1) > r.shift(2))
    e = c.ewm(span=int(p["emaLength"]), adjust=False).mean()
    le = crossed & was_os & hook_up & (c < e)
    se = crossed & was_ob & hook_dn & (c > e)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
