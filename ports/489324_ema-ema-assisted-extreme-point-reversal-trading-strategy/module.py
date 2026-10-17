"""CCI zero crosses after RSI extremes with an RSI turn, on the far side of EMA 100, always in, three-day bars: a CCI 10
zero cross (either way, as written) within four bars of RSI 14 <= 35, with the RSI turning up and the close below EMA
100, goes long; the mirror after RSI >= 65 above EMA 100 goes short.
Port of FMZ strategy #489324 "EMA辅助极点反转交易策略-EMA-Assisted-Extreme-Point-Reversal-Trading-Strategy" (Extreme Points + 100 EMA Strategy).

FMZ source id: 489324

Source
    https://www.fmz.com/strategy/489324 (PineScript v5, FMZ last modified 2025-04-03 14:50:24).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 176-218), CCI 10, RSI 14 (35 / 65), EMA 100, divergence check on
    crossUp = ta.cross(cci, 0);  crossDown = ta.cross(0, cci)   (ta.cross is true for a cross in either direction)
    oversoldAgo = rsi <= 35 on any of the last 4 bars;  bullTurn = rsi > rsi[1] and rsi[1] < rsi[2]
    long = crossUp and oversoldAgo and bullTurn and close < ema100;  short = crossDown and overboughtAgo and bearTurn and close > ema100

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.cross fires on a cross either way, so both "up" and "down" are any CCI zero cross, as written.
    * CCI = (close - SMA 10) / (0.015 x mean absolute deviation over 10); the RSI is the source's own formula.
    * No exit other than the opposite entry: always in after the first signal (REVERSAL INTENDED). A long and a short
      cannot fall on one bar (the RSI turns oppose).
    * FREQ = "3D" from the backtest header (period 3d): three-day bars from broker days in fixed blocks of three
      broker-day dates counted from 1970-01-01 (block phase: decision owed), as #426509.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillators and an EMA.
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

NAME = "fmz_489324_cci_cross_rsi_extreme_ema100"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_oversold": [35, 30],
    "use_divergence": [True, False],
}
DEFAULT_PARAMS = {"cci_len": 10, "rsi_len": 14, "rsi_overbought": 65, "rsi_oversold": 35, "ema_len": 100,
                  "use_divergence": True}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, days=3):
    """Blocks of `days` broker-day dates counted from 1970-01-01, stamped with the first session start (#426509)."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


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
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _cci(c, n):
    sma = c.rolling(n).mean()
    mad = c.rolling(n).apply(lambda w: np.abs(w - w.mean()).mean(), raw=True)
    return (c - sma) / (0.015 * mad)


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=3)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    cci = _cci(c, int(p["cci_len"]))
    cross = ((cci > 0) & (cci.shift(1) <= 0)) | ((cci < 0) & (cci.shift(1) >= 0))
    rsi = _rsi(c, int(p["rsi_len"]))
    os_ago = (rsi <= p["rsi_oversold"]).astype(int).rolling(4, min_periods=1).max() > 0
    ob_ago = (rsi >= p["rsi_overbought"]).astype(int).rolling(4, min_periods=1).max() > 0
    bull_turn = (rsi > rsi.shift(1)) & (rsi.shift(1) < rsi.shift(2))
    bear_turn = (rsi < rsi.shift(1)) & (rsi.shift(1) > rsi.shift(2))
    if not p["use_divergence"]:
        bull_turn = bear_turn = pd.Series(True, index=c.index)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    long_e = (cross & os_ago & bull_turn & (c < ema)).astype(bool)
    short_e = (cross & ob_ago & bear_turn & (c > ema) & ~long_e).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
