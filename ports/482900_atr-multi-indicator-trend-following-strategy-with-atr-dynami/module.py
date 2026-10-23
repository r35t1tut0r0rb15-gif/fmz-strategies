"""Broker days: the EMA 9 crossing over the EMA 21 with RSI 14 under 70, above-average volume and a close above the previous high goes long; the mirror goes short; each trade gets a 1.5 ATR 14 stop and a 3 ATR target from the signal close; reversing.
Port of FMZ strategy #482900 "多指标趋势跟踪策略结合ATR动态止盈止损-Multi-Indicator-Trend-Following-Strategy-with-ATR-Dynamic-Stop-Loss-Take-Profit" (15m EMA RSI Strategy with ATR SL/TP and Candle Break Confirmation).

FMZ source id: 482900

Source
    https://www.fmz.com/strategy/482900 (PineScript v6, FMZ last modified 2025-02-27 17:27:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 114-169), EMA 9 / 21; RSI 14 (70 / 30); volume SMA 20; candle break; ATR 14; SL 1.5, TP 3 ATR; trail_points = ATR (no offset)
    longCondition = crossover(ema9, ema21) and rsi < 70 and volume > volMA and close > high[1] -> entry Long, exit(stop = close - 1.5 atr, limit = close + 3 atr, trail_points = atr)
    shortCondition mirrored (rsi > 30, close < low[1]) -> entry Short, exit(stop = close + 1.5 atr, limit = close - 3 atr, trail_points = atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * trail_points (an activation distance, here a price amount passed as ticks) without a trail_offset
      places no trailing stop (as #441084), so the exits are the stop and the target, sent on signal bars
      as levels from that close: ported as fractions of the fill, exact (1e-6 floor). Titled 15-minute;
      the header is 1 day. The header names TRB_USDT; the rules are generic. REVERSAL INTENDED. 10 % of
      equity is sizing. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars:
      coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, EMA crossings confirmed by RSI, volume and a candle break.
    3 crypto-exchange-only: no (exchange pair in the header only (TRB_USDT)).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482900_ema9_21_cross_rsi_volume_candle_break_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [1.5, 2.0],
    "tp_atr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"sl_atr": 1.5, "tp_atr": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def simulate(bars_df, **params):
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    f, s = c.ewm(span=9, adjust=False).mean(), c.ewm(span=21, adjust=False).mean()
    r = _rsi(c, 14)
    vol_ok = v > v.rolling(20).mean()
    buy = (f > s) & (f.shift(1) <= s.shift(1)) & (r < 70) & vol_ok & (c > h.shift(1))
    sell = (f < s) & (f.shift(1) >= s.shift(1)) & (r > 30) & vol_ok & (c < lo.shift(1))
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
