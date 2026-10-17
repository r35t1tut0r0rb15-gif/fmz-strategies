"""Closes above the SMA 30 with MACD (9 / 18 / 9) above its signal and zero and ADX above 25 go long; once the close
is below the SMA, a stop at the second-last swing low recorded during the trade ends it, long only, daily bars.
Port of FMZ strategy #482793 "基于趋势确认的多重指标动态止损策略-Trend-Confirmation-Multi-Indicator-Dynamic-Stop-Loss-Strategy" (Invest SMA|MACD|ADX Long Weekly Strategy (BtTL)).

FMZ source id: 482793

Source
    https://www.fmz.com/strategy/482793 (PineScript v5, FMZ last modified 2025-02-20 11:19:58).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 104-148), SMA 30, MACD 9 / 18 / 9, DMI 14 / ADX 14 > 25
    long = close > sma and macd > signal and macd > 0 and adx > 25 -> entry long
    isSwingLow = low[2] > low[1] and low[3] > low[1] and low[1] < low and low[1] < low[4];
    isSwingLow[1] -> secondLast := last, last := low[1]
    close < sma and secondLast known -> exit(stop = secondLast) (re-issued while that holds)
    flat -> both swing lows forgotten

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop level exists only after two swing lows are recorded during the trade and moves when new ones arrive,
      so the house bracket (fixed at the fill) cannot carry it: simulate() keeps the Pine order (placed at a bar's
      close, active from the next bar, replaced while the close stays under the SMA, kept once placed) and emits an
      exit signal on the bar whose low reaches it, filled at the next open (one bar later than Pine's stop fill; a
      level placed at or above the close exits at the next open, as Pine would). Mark trailing_stop_pending.
    * lastSwingLow takes low[1] of the bar after the swing (as written), not the swing bar's own low.
    * Every bar in the condition is an entry signal (ignored while held). On a bar where the stop is reached the
      entry is not emitted (it would meet the exit on one bar); Pine could re-enter there.
    * DMI / ADX as ta.dmi (#426579). Long only. Signal module, no stops. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the late swing-low stop as an exit signal (marked).
    2 generic: PASS, an SMA, MACD, ADX and swing lows.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482793_sma_macd_adx_long_swing_low_stop"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [30, 50],
    "adx_min": [25.0, 20.0],
}
DEFAULT_PARAMS = {"sma_len": 30, "fast": 9, "slow": 18, "signal": 9, "di_len": 14, "adx_len": 14, "adx_min": 25.0}


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


def _fixnan(v):
    """Pine fixnan: replace na by the last non-na value (past values only)."""
    out = np.array(v, dtype=float)
    for i in range(1, len(out)):
        if np.isnan(out[i]):
            out[i] = out[i - 1]
    return out


def _adx_pine(bars, di_len, adx_len):
    """Pine's built-in-style dirmov/adx: RMA smoothing, fixnan on DI+/DI-."""
    h, lo, c = bars["high"], bars["low"], bars["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > down) & (up > 0), up, 0.0))
    minus_dm = np.where(down.isna(), np.nan, np.where((down > up) & (down > 0), down, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trs = _rma(tr, di_len)
    plus = _fixnan((100 * _rma(pd.Series(plus_dm, index=h.index), di_len) / trs).to_numpy())
    minus = _fixnan((100 * _rma(pd.Series(minus_dm, index=h.index), di_len) / trs).to_numpy())
    s = plus + minus
    dx = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1, s), index=h.index)
    return pd.Series(plus, index=h.index), pd.Series(minus, index=h.index), 100 * _rma(dx, adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lo_s, c = bars_df["low"], bars_df["close"]
    sma = c.rolling(int(p["sma_len"])).mean()
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    _, _, adx = _adx_pine(bars_df, int(p["di_len"]), int(p["adx_len"]))
    buy = ((c > sma) & (macd > sig) & (macd > 0) & (adx > p["adx_min"])).to_numpy()
    below = (c < sma).to_numpy()
    l1 = lo_s.shift(1)
    swing = ((lo_s.shift(2) > l1) & (lo_s.shift(3) > l1) & (l1 < lo_s) & (l1 < lo_s.shift(4)))
    swing_prev = swing.shift(1, fill_value=False).to_numpy()          # isSwingLow[1]
    lo, cv = lo_s.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    last = second = stop = np.nan
    for i in range(m):
        hit = pos == 1 and entry_i <= i and not np.isnan(stop) and lo[i] <= stop
        if hit:                                   # the resting stop is reached on this bar
            lx[i], pos, stop = True, 0, np.nan
        if swing_prev[i]:
            second, last = last, lo[i - 1]
        if buy[i] and pos == 0 and not hit and i + 1 < m:
            le[i], pos, entry_i = True, 1, i + 1
        held_now = pos == 1 and entry_i <= i      # strategy.position_size > 0 at this bar's close
        if held_now and below[i] and not np.isnan(second):
            stop = second
            if cv[i] <= stop:                     # placed at or above the close: filled at the next open
                lx[i], pos, stop = True, 0, np.nan
                held_now = False
        if not held_now:
            last = second = np.nan
            if pos == 0:
                stop = np.nan
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
