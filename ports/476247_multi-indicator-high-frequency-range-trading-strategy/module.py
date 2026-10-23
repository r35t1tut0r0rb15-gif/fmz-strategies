"""Broker days: the EMA 8 crossing over the EMA 21 with RSI 14 over 50, volume above its 20-day average and the 5-bar low above the 10-bar low goes long; the mirror goes short; each trade gets a 1.5 % target and a 0.7 % stop from the signal close; reversing.
Port of FMZ strategy #476247 "Multi Indicator High Frequency Range Trading Strategy" (XRP/USD Scalping Strategy with Alerts).

FMZ source id: 476247

Source
    https://www.fmz.com/strategy/476247 (PineScript v5, FMZ last modified 2024-12-27 14:18:57).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 107-154), EMA 8 / 21; RSI 14 vs 50; volume SMA 20; n-bars 5 / 10; TP 1.5 %, SL 0.7 % from the signal close
    long_condition = crossover(ema8, ema21) and rsi > 50 and volume > avg_volume and lowest(low, 5) > lowest(low, 10) -> entry Long, exit("TP/SL", "Long", limit = close x 1.015, stop = close x 0.993)
    short mirrored (highest(high, 5) < highest(high, 10)) -> entry Short, exit(same id, "Short", limit = close x 0.985, stop = close x 1.007)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars only, as levels from that close: ported as fractions of the
      fill, exact (1e-6 floor). Both sides share one exit id, but the calls only happen on their own
      signal bars (which never coincide), so each trade keeps its own bracket until the opposite entry
      reverses it. The title names XRP/USD and scalping; the header is 1-day BTC_USDT. REVERSAL
      INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars:
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket at the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings with RSI, volume and higher-low filters.
    3 crypto-exchange-only: no (exchange pair in the header only (XRP/USD named in the title)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_476247_ema8_21_cross_rsi_volume_nbar_1_5_0_7pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.015, 0.03],
    "sl": [0.007, 0.015],
}
DEFAULT_PARAMS = {"n_bars": 5, "tp": 0.015, "sl": 0.007}


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
    f, s = c.ewm(span=8, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean()
    k = int(p["n_bars"])
    bull = lo.rolling(k).min() > lo.rolling(2 * k).min()
    bear = h.rolling(k).max() < h.rolling(2 * k).max()
    buy = (f > s) & (f.shift(1) <= s.shift(1)) & (r > 50) & vol_ok & bull
    sell = (f < s) & (f.shift(1) >= s.shift(1)) & (r < 50) & vol_ok & bear
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o
    sl, tp = float(p["sl"]), float(p["tp"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - sl))
            .mask(sf, k * (1 + sl) - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, k * (1 + tp) - 1)
            .mask(sf, 1 - k * (1 - tp)))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
