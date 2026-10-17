"""Liquidity touch + internal market shift, entries from flat, broker days: after the low touches its 10-bar low, a
close above the high of the last bearish run (and above the run before it) goes long; mirrored for shorts after the
high touches its 10-bar high; an opposite signal closes the trade, and so do close-checked stop / target levels a few
ticks from the entry close.
Port of FMZ strategy #488536 "动态流动性驱动市场结构自适应交易策略-Dynamic-Liquidity-Driven-Market-Structure-Adaptive-Trading-Strategy" (Liquidity + Internal Market Shift Strategy).

FMZ source id: 488536

Source
    https://www.fmz.com/strategy/488536 (PineScript v6, FMZ last modified 2025-03-28 17:13:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 118-342), mode Both, liquidity lookbacks 10 / 10, SL 10 ticks, TP 20 ticks
    bullish / bearish runs track the run's lowest low / highest high; previousBullishPrice / previousBearishPrice
    internalShiftBullish = close > previousBearishPrice and close > highestBearishPrice (bearish mirrored)
    touchedLower = low <= lowest(low, 10) (latched); bullishSignal = shift and touchedLower and not lockedBullish
    (locks set on a signal, released after 3 bars or by a new touch)
    bearishSignal and flat -> entry short; bullishSignal and flat -> entry long (the script's own entryPrice gate)
    long and bearishSignal -> close; close <= entry - 10 ticks or close >= entry + 20 ticks -> close (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * lastInternalShift is never assigned (always 0), so the allow-filters always pass, as written.
    * A bullish shift needs a close above a bearish run's high, impossible on a bearish bar (close < open <= high), and
      vice versa, so the two signals never fall on one bar.
    * Entries only from flat (the script's entryPrice gate), so opposite entries cannot occur: an opposite signal
      while held closes the trade and the next signal opens the next one.
    * Criterion 2: on the author's daily ETH_USDT (tick 0.01, daily ATR about 100-150) 10 / 20 ticks are about
      0.001 / 0.002 Wilder ATR(14) (judgement before any backtest): sl_atr x ATR of the entry bar, the target
      tp_mult x that, fixed for the trade. The levels are close-checked: exit signals at the next open (rule 3), no
      stop module. As written nearly every next close crosses one of them (a one-bar hold).
    * The mode input is a GRID variant (Both / Bullish Only). Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked exits.
    2 generic: ADAPT, tick distances -> ATR multiples; candle runs and rolling extremes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick levels quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_488536_liquidity_internal_shift"
FAMILY = "market_structure_shift"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mode": ["Both", "Bullish Only"],
    "sl_atr": [0.001, 1.0],
}
DEFAULT_PARAMS = {"mode": "Both", "upper_lookback": 10, "lower_lookback": 10, "enable_tp": True, "sl_atr": 0.001,
                  "tp_mult": 2.0, "atr_len": 14}


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
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    hh = bars_df["high"].rolling(int(p["upper_lookback"])).max().to_numpy(dtype=float)
    ll = bars_df["low"].rolling(int(p["lower_lookback"])).min().to_numpy(dtype=float)
    atr = _atr(bars_df, int(p["atr_len"])).to_numpy(dtype=float)
    allow_long = p["mode"] in ("Both", "Bullish Only")
    allow_short = p["mode"] in ("Both", "Bearish Only")
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    bull_n = bear_n = 0
    low_bull = high_bear = prev_bull = prev_bear = np.nan
    touch_lo = touch_hi = lock_bull = lock_bear = False
    since = None
    side, entry, dist = 0, np.nan, np.nan
    for i in range(m):
        if c[i] > o[i]:
            bull_n, bear_n = bull_n + 1, 0
            if bull_n == 1 or lo[i] < low_bull:
                low_bull = lo[i]
        elif c[i] < o[i]:
            bear_n, bull_n = bear_n + 1, 0
            if bear_n == 1 or h[i] > high_bear:
                high_bear = h[i]
        else:
            bull_n = bear_n = 0
            low_bull = high_bear = np.nan
        shift_bear = c[i] < prev_bull and c[i] < low_bull       # NaN comparisons are False, as Pine's na
        shift_bull = c[i] > prev_bear and c[i] > high_bear
        if bull_n >= 1:
            prev_bull = low_bull
        if bear_n >= 1:
            prev_bear = high_bear
        if lo[i] <= ll[i]:
            touch_lo = True
        if h[i] >= hh[i]:
            touch_hi = True
        bull_sig = shift_bull and touch_lo and not lock_bull
        bear_sig = shift_bear and touch_hi and not lock_bear
        if bull_sig:
            lock_bull, touch_lo, since = True, False, 0
        if bear_sig:
            lock_bear, touch_hi, since = True, False, 0
        if since is not None:
            since += 1
        if since is not None and since >= 3:
            lock_bull = lock_bear = False
        if touch_lo:
            lock_bull = False
        if touch_hi:
            lock_bear = False
        prev = side
        if allow_short and bear_sig and side == 0:
            side, entry, dist = -1, c[i], p["sl_atr"] * atr[i]
        if allow_long and bull_sig and side == 0:
            side, entry, dist = 1, c[i], p["sl_atr"] * atr[i]
        if side == -1 and bull_sig:
            side = 0
        if side == 1 and bear_sig:
            side = 0
        if side == 1 and (c[i] <= entry - dist or (p["enable_tp"] and c[i] >= entry + p["tp_mult"] * dist)):
            side = 0
        if side == -1 and (c[i] >= entry + dist or (p["enable_tp"] and c[i] <= entry - p["tp_mult"] * dist)):
            side = 0
        if side != prev:
            le[i] = side == 1
            se[i] = side == -1
            lx[i] = prev == 1 and side == 0
            sx[i] = prev == -1 and side == 0
    idx = bars_df.index
    return tuple(pd.Series(x, index=idx) for x in (le, lx, se, sx))


def portfolio_kwargs(**params):
    return {}
