"""2-day bars: two bars in a row closing 1 % beyond the upper Bollinger band (20, 2) with RSI 14 above 50, volume above its 20-bar average and the close above the EMA 200 go long (the mirror below the lower band goes short); each trade gets a 1.5 ATR stop and a 2.25 ATR target from the signal close; reversing.
Port of FMZ strategy #474844 "Enhanced Bollinger Breakout Quantitative Strategy with Momentum Filter Integration System" (Improved Bollinger Breakout with Trend Filtering).

FMZ source id: 474844

Source
    https://www.fmz.com/strategy/474844 (PineScript v5, FMZ last modified 2024-12-12 14:55:37).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 134-191), BB 20 x 2 (x 1.01 / 0.99); RSI 14 vs 50; volume SMA 20; EMA 200; 2 confirming bars; ATR 14 x 1.5, RR 1.5
    long_raw = close > upper x 1.01 and rsi > 50 and volume > sma(volume, 20) and close > ema200;  long_condition = long_raw on this bar and the one before
    long_condition -> entry Long, exit("Exit Long", "Long", stop = close - 1.5 atr, limit = close + 2.25 atr)  (short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars, as levels from that close: ported as fractions of the fill,
      exact (1e-6 floor). The condition stays true on consecutive bars of a strong run, and each repeat
      while in the trade re-sends the bracket from the new bar's close (not followed:
      trailing_stop_pending). Pine's stdev is the population deviation. 2-day bars are blocks of two
      broker days counted from 1970-01-01, each stamped with its first minute. REVERSAL INTENDED. No
      sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-day bars: coarse_bar_stop.
      FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, confirmed Bollinger breakouts in the EMA 200 trend on volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per 2-day bar) against its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker days in 2-day blocks (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474844_confirmed_bollinger_breakout_ema200_volume_atr_bracket_2d_reversal"
FAMILY = "bollinger_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (two broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "confirm": [2, 1],
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"days": 2, "length": 20, "mult": 2.0, "confirm": 2, "atr_mult": 1.5, "rr": 1.5}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    n = int(p["length"])
    basis, dev = c.rolling(n).mean(), float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean()
    ema = c.ewm(span=200, adjust=False).mean()
    lr = (c > (basis + dev) * 1.01) & (r > 50) & vol_ok & (c > ema)
    sr = (c < (basis - dev) * 0.99) & (r < 50) & vol_ok & (c < ema)
    k = int(p["confirm"])
    buy, sell = lr.copy(), sr.copy()
    for i in range(1, k):
        buy &= lr.shift(i, fill_value=False)
        sell &= sr.shift(i, fill_value=False)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d = float(p["atr_mult"]) * atr
    tp_d = sl_d * float(p["rr"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
