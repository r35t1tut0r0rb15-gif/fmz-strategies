"""Broker days: a close within 2 % above the 30-day low (the current day included) with RSI 14 under 30 and volume above its 20-day average goes long; a close within 2 % below the 30-day high with RSI over 70 on the same volume test goes short; no other exit; reversing.
Port of FMZ strategy #489731 "Multi Indicator Fusion Support Resistance Volume Filtered Quantitative Trading Strategy" (SMA + RSI + S/R Strategy with Filters).

FMZ source id: 489731

Source
    https://www.fmz.com/strategy/489731 (PineScript v5, FMZ last modified 2025-04-08 09:46:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 202-244), support / resistance = lowest low / highest high of 30 bars (current included); RSI 14 (30 / 70); volume > SMA 20; SMA 50 plotted only; 100 % of equity
    buySignal = close <= support x 1.02 and rsi < 30 and volume > sma(volume, 20) -> entry Buy;  sellSignal = close >= resistance x 0.98 and rsi > 70 and the volume test -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The windows include the current bar, as written. There is no exit: an opposite entry reverses, so
      the strategy stays in the market after the first signal. REVERSAL INTENDED. 100 % of equity is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ =
      "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oversold closes near support and overbought closes near resistance on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489731_near_30d_support_resistance_rsi_volume_reversal"
FAMILY = "oscillator_reversion"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sr_window": [30, 20],
    "near_pct": [2.0, 1.0],
}
DEFAULT_PARAMS = {"sr_window": 30, "near_pct": 2.0}


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
    n = int(p["sr_window"])
    k = float(p["near_pct"]) / 100
    sup, res = lo.rolling(n).min(), h.rolling(n).max()
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean()
    le = (c <= sup * (1 + k)) & (r < 30) & vol_ok
    se = (c >= res * (1 - k)) & (r > 70) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return le.astype(bool), false, se.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
