"""Quickfingers-style base cracks: after a wide-range ("panic") move has been seen, a low 0.5 % under the 50-bar lowest
close goes long (5-bar cooldown between signals); closed when a close is 1 % above the entry and above the rebound
level, long only, daily bars.
Port of FMZ strategy #482512 "QFL震荡条件止损均线策略-QFL-Oscillation-Stop-Loss-Moving-Average-Strategy" (Jackson Quickfingersluc (QFL) Strategy).

FMZ source id: 482512

Source
    https://www.fmz.com/strategy/482512 (PineScript v6, FMZ last modified 2025-02-18 18:18:01).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 92-207), base x 1, rebound x 0.8, look-back 50, ATR 14 x 1.2, profit 1 %,
panic 0.5 %, range 3 bars, cooldown 5, take profit "avg_price"
    base = lowest(close, 50)[1]; rebound = 0.8 x (highest(high, 3) - lowest(low, 3)) + base
    panic movement (var, never reset): for k = 1..4, (highest(high, k) - lowest(low, k)) / k > 1.2 ATR or
    high[k-1] - low[k-1] > 1.2 ATR
    entry = low < base x 0.995 and panic movement and more than 5 bars since the last signal -> entry long
    (close - position_avg_price) / position_avg_price >= 1 % and close > rebound -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * panicSellMovement is a var set true and never reset: after the first wide move it stays true (as written).
    * The cooldown counts from every signal bar (lastEntryBar is set even when the entry meets an open position).
    * With pyramiding 1 the average price is the fill price; the take profit is tested on closes with
      strategy.close: an exit signal at the next open (rule 3). The "each_position" option (partial closes) is not
      the default and is not ported.
    * Long only; no stop. Signal module. Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a close-based take profit.
    2 generic: PASS, rolling extremes, ATR multiples and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482512_qfl_base_crack_rebound_exit_long"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [50, 20],
    "profit": [0.01, 0.03],
}
DEFAULT_PARAMS = {"lookback": 50, "rebound_mult": 0.8, "atr_len": 14, "atr_mult": 1.2, "profit": 0.01,
                  "panic_pct": 0.005, "range_bars": 3, "cooldown": 5}


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
    base = c.rolling(int(p["lookback"])).min().shift(1)
    rb = int(p["range_bars"])
    rebound = p["rebound_mult"] * (h.rolling(rb).max() - lo.rolling(rb).min()) + base
    lim = p["atr_mult"] * _atr(bars_df, int(p["atr_len"]))
    wide = pd.Series(False, index=c.index)
    for k in range(1, rb + 2):
        wide |= ((h.rolling(k).max() - lo.rolling(k).min()) / k > lim) | ((h - lo).shift(k - 1) > lim)
    crack = (lo < base * (1 - p["panic_pct"])).to_numpy()
    wide_v, cv, rbv = wide.to_numpy(), c.to_numpy(dtype=float), rebound.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    panic, last = False, None
    held, pending, entry_px = False, False, np.nan
    for i in range(m):
        if pending:
            held, pending, entry_px = True, False, ov[i]       # filled at this bar's open
        panic = panic or bool(wide_v[i])
        if crack[i] and panic and (last is None or i - last > int(p["cooldown"])):
            last = i
            if not held and i + 1 < m:
                le[i], pending = True, True
        if held and (cv[i] - entry_px) / entry_px >= p["profit"] and cv[i] > rbv[i]:
            lx[i], held = True, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
