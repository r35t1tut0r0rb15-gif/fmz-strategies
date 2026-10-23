"""Broker days: a close above the EMA 50 on volume above 1.5 x its 20-day average and above the previous day's volume goes long, a close below it on such volume goes short; each trade gets a 2 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #478745 "Advanced Multi Indicator Trend Confirmation Trading Strategy" (Enhanced Volume + Trend Strategy).

FMZ source id: 478745

Source
    https://www.fmz.com/strategy/478745 (PineScript v5, FMZ last modified 2025-01-17 16:33:07).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 88-139), EMA 50; volume SMA 20 x 1.5 and > volume[1]; ATR 14; SL 2 ATR, TP 3 ATR
    longCondition = close > ema50 and volume > volMA x 1.5 and volume > volume[1] -> entry Long, exit("Take Profit/Stop Loss", "Long", stop = close - 2 atr, limit = close + 3 atr)
    shortCondition = close < ema50 and the same volume test -> entry Short, exit(same id, "Short", stop = close + 2 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on signal bars, as levels from that close: ported as fractions of the fill,
      exact (1e-6 floor). Both sides share one exit id, but a long and a short signal never meet on one
      bar, so each trade keeps its own bracket until the opposite entry reverses it; a repeated signal
      while in the trade re-sends it from the new close (not followed: trailing_stop_pending). The
      entries are states, so after a stop or target the strategy re-enters on the next qualifying bar.
      REVERSAL INTENDED. No sizing code. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, EMA 50 side on rising high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against 1.5 x its SMA 20 and the previous day's; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_478745_ema50_side_rising_volume_atr_bracket_reversal"
FAMILY = "volume_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [50, 100],
    "vol_mult": [1.5, 2.0],
}
DEFAULT_PARAMS = {"ema_len": 50, "vol_mult": 1.5, "sl_atr": 2.0, "tp_atr": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, v = bars_df["close"], bars_df["volume"]
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    vol_ok = (v > v.rolling(20).mean() * float(p["vol_mult"])) & (v > v.shift(1))
    buy = (c > ema) & vol_ok
    sell = (c < ema) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
