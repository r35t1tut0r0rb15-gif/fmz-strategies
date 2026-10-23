"""Broker days: three up candles in a row with volume 1.5 times its 3-bar average and the close above the EMA 200 goes long, with a stop 1.5 ATR 14 under the bar's low and a target 2.5 ATR over its high; the mirror goes short; reversing.
Port of FMZ strategy #457794 "Enhanced Multi Indicator Momentum Trading Strategy" (Improved Volume Based Strategy).

FMZ source id: 457794

Source
    https://www.fmz.com/strategy/457794 (PineScript v5, FMZ last modified 2024-07-26 16:20:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 156-200), volume period 3, ratio 1.5; ATR 14, SL x 1.5, TP x 2.5; EMA 200
    longCondition = 3 up candles and volume / sma(volume, 3) > 1.5 and close > ema200 -> entry Long, exit(stop = low - 1.5 atr, limit = high + 2.5 atr)
    shortCondition = 3 down candles and ratio > 1.5 and close < ema200 -> entry Short, exit(stop = high + 1.5 atr, limit = low - 2.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars, as levels from that bar's low / high and ATR: ported as
      fractions of the fill (1e-6 floor); a repeated signal while in the position re-sends it from the
      new bar, which the port does not follow (mark trailing_stop_pending). "volumeUp" is just an up candle. REVERSAL INTENDED. No
      sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal bar as fractions of the fill.
    2 generic: PASS, three-candle runs on a volume surge with an EMA 200 filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) over its 3-bar average; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_457794_three_candle_run_volume_surge_ema200_atr_bracket_reversal"
FAMILY = "momentum_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "vol_ratio": [1.5, 2.0],
    "tp_atr": [2.5, 4.0],
}
DEFAULT_PARAMS = {"vol_period": 3, "vol_ratio": 1.5, "atr_len": 14, "sl_atr": 1.5, "tp_atr": 2.5, "ema_len": 200}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    up, dn = c > o, c < o
    run_up = up & up.shift(1, fill_value=False) & up.shift(2, fill_value=False)
    run_dn = dn & dn.shift(1, fill_value=False) & dn.shift(2, fill_value=False)
    sv = v.rolling(int(p["vol_period"])).mean()
    surge = v / sv.where(sv != 0) > float(p["vol_ratio"])
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    lg = run_up & surge & (c > ema)
    sh = run_dn & surge & (c < ema)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return lg.astype(bool), false, sh.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["atr_len"]))
    sa, ta = float(p["sl_atr"]), float(p["tp_atr"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (lo - sa * atr).shift(1) / o)
            .mask(sf, (h + sa * atr).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (h + ta * atr).shift(1) / o - 1)
            .mask(sf, 1 - (lo - ta * atr).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
