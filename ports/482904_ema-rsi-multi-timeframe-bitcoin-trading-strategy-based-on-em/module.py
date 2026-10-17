"""Weekly EMA 20 regime filter with a 7-bar swing trailing exit, long only, daily (broker-day) bars: from flat, when
the previous day's close is above the last completed week's EMA 20 plus 0.25 ATR(5) and the bar is not a wide-range
"caution" bar, go long; close when the close falls below a ratcheting stop (the 7-bar highest low minus 1 ATR) or
below the weekly EMA.
Port of FMZ strategy #482904 "基于多重级别EMA与RSI动态势能强度的比特币跨周期趋势交易策略-Multi-Timeframe-Bitcoin-Trading-Strategy-Based-on-EMA-and-RSI-Dynamic-Momentum-Strength" (Bitcoin Regime Filter Strategy).

FMZ source id: 482904

Source
    https://www.fmz.com/strategy/482904 (PineScript v6, FMZ last modified 2025-02-27 17:24:26).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 115-181), weekly EMA 20, ATR 5, RSI filter off
    htfEma = f_sec("W", ema(close, 20)); marketPrice = f_sec("D", close) (= the previous daily close on history)
    bullish = marketPrice > htfEma + 0.25 ATR; caution = bullish and highest(high, 7) - low > 1.5 ATR
    entry long when bullish, flat and not caution (trail reset); while long: trail = max(trail, highest(low, 7) -
    (caution[1] ? 0.2 ATR : ATR)); close when close < trail or close < htfEma

Interpretation choices (Pine rules in SURVEY_README.md)
    * f_sec on history returns security(...)[1]: the daily close is the previous bar's close; the weekly EMA is taken
      from the last COMPLETED week (house request.security rule), weeks of broker days built from the port's own bars.
    * The trail and the weekly-EMA exit are checked on closes through strategy.close: exit signals at the next open
      (rule 3), no broker stop. Entries only from flat (position_size == 0 at the bar's close): state machine on the
      position held at each close; the close never undoes that bar's entry.
    * The RSI momentum filter is off by default (kept off). Long only. Daily bars are broker days (17:00
      America/New_York) stamped with their first minute (as #430984). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; completed weekly values; close-based exits as exit signals.
    2 generic: PASS, EMAs, ATR multiples and rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone) for the daily and weekly bars; no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482904_weekly_ema_regime_swing_trail_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_len": [20, 10],
    "atr_len": [5, 14],
}
DEFAULT_PARAMS = {"ema_len": 20, "atr_len": 5, "swing": 7}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    wk = pd.DatetimeIndex(broker_day(bars_df.index)).to_period("W")
    weekly = pd.Series(c.to_numpy(), index=wk).groupby(level=0).last()
    w_ema = weekly.ewm(span=int(p["ema_len"]), adjust=False).mean()
    htf = w_ema.shift(1).reindex(wk).to_numpy()              # the last completed week
    atr = _atr(bars_df, int(p["atr_len"])).to_numpy()
    n = int(p["swing"])
    hh7 = h.rolling(n).max().to_numpy()
    hl7 = lo.rolling(n).max().to_numpy()
    cv, lv, prev_c = c.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.shift(1).to_numpy()
    bullish = prev_c > htf + atr * 0.25
    caution = bullish & ((hh7 - lv) > atr * 1.5)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held, trail = 0, np.nan
    for i in range(m):
        pos = held                                   # position at this bar's close (fills at its open)
        if bullish[i] and held == 0 and not caution[i]:
            pos, trail = 1, np.nan
        if held == 1:
            k = 0.2 if (i > 0 and caution[i - 1]) else 1.0
            tmp = hl7[i] - atr[i] * k
            if np.isnan(trail) or tmp > trail:
                trail = tmp
        if held == 1 and (cv[i] < trail or cv[i] < htf[i]):
            pos = 0
        tgt[i] = pos
        held = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return (pd.Series((tgt == 1) & (prev == 0), index=idx), pd.Series((tgt == 0) & (prev == 1), index=idx),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
