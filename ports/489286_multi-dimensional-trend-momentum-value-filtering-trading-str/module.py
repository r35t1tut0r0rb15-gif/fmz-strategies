"""Broker days: the script's ADX 14 over 25 with RSI 14 under 30, stochastic RSI 14 under 20 and the close under the day's VWAP of hlc3 (the bar's own hlc3) goes long; ADX over 25 with RSI over 70, stochastic RSI over 80 and the close above it goes short; no other exit; reversing.
Port of FMZ strategy #489286 "Multi Dimensional Trend Momentum Value Filtering Trading Strategy" (BuySell Strategy OD).

FMZ source id: 489286

Source
    https://www.fmz.com/strategy/489286 (PineScript v5, FMZ last modified 2025-04-03 15:16:18).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 186-237), RSI 14; stoch RSI 14 (20 / 80); manual ADX 14 (> 25; true range without abs); session VWAP of hlc3
    buyCond = adx > 25 and rsi < 30 and stochRsi < 20 and close < vwap(hlc3) -> entry BUY;  sellCond = adx > 25 and rsi > 70 and stochRsi > 80 and close > vwap -> entry SELL

Interpretation choices (Pine rules in SURVEY_README.md)
    * On 1-day bars the session VWAP of hlc3 has one bar per session, so it is that bar's hlc3: the
      tests are the close against the bar's own typical price, and the volume cancels (it matters only
      when it is 0). The script's true range is max(high - low, high - close[1], low - close[1]) without
      abs, as written. There is no exit: an opposite entry reverses. stochRsi is 0 when the 14-bar RSI
      range is flat or na (Pine). REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI / stochastic RSI extremes in a strong ADX, against the bar's typical price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used only as a common factor: the session VWAP of a one-bar session is the bar's hlc3 x volume / volume (broker tick volume of the cTrader M1 data, summed per broker day; only a zero volume changes it); exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); one bar per VWAP session.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489286_adx_rsi_stochrsi_extreme_vs_daily_hlc3_reversal"
FAMILY = "oscillator_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [25.0, 20.0],
    "rsi_lo": [30.0, 25.0],
}
DEFAULT_PARAMS = {"adx_min": 25.0, "rsi_lo": 30.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    r = _rsi(c, 14)
    rmin, rmax = r.rolling(14).min(), r.rolling(14).max()
    stoch = ((r - rmin) / (rmax - rmin) * 100).where(rmin.notna() & rmax.notna() & (rmax != rmin), 0.0)
    up, dn = h - h.shift(1), lo.shift(1) - lo
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, h - pc, lo - pc], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, 14)
    pdi, mdi = 100 * _rma(pdm, 14) / atr, 100 * _rma(mdm, 14) / atr
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), 14)
    day = broker_day(bars_df.index)
    hlc3 = (h + lo + c) / 3
    vw = (hlc3 * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    lo_r = float(p["rsi_lo"])
    strong = adx > float(p["adx_min"])
    le = strong & (r < lo_r) & (stoch < 20) & (c < vw)
    se = strong & (r > 100 - lo_r) & (stoch > 80) & (c > vw)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
