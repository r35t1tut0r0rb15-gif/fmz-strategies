"""UT Bot crosses (1.1 x ATR 200 trail) on the EMA 50 side, with the stop moved to the entry price once a close is
20 % in profit, daily bars: a close crossing above the UT trail above the EMA goes long, below it below the EMA short.
Port of FMZ strategy #482822 "ATR动态追踪止损的趋势跟踪交易系统-ATR-Dynamic-Trailing-Stop-Trend-Following-Trading-System" (Enhanced UT Bot with Long & Short Trades).

FMZ source id: 482822

Source
    https://www.fmz.com/strategy/482822 (PineScript v5, FMZ last modified 2025-02-20 14:53:21).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 118-201), key 1.1, ATR 200, EMA 50, ROI close 100 %
    UT trail (nz-seeded, as L1 #492009); buy = crossover(close, trail) and close > ema; sell mirrored
    buy and position <= 0 -> entry long; sell and position > 0 -> close long; sell and position >= 0 -> entry short;
    buy and position < 0 -> close short
    while held, on the bar's close profit: >= 20 % -> exit(stop = entry); >= 50 % -> exit(stop = 1.3 x entry) and
    close("Partial Profit", 50 %); >= 80 % -> exit(stop = 1.6 x entry); >= 100 % -> close("Full Exit at 100% ROI")
    (shorts mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes "Partial Profit" and "Full Exit at 100% ROI" name no entry ("Buy" / "Sell"), so they never act
      (as written): no partial exit, no ROI exit.
    * The position tests use the position at the bar's start, so a signal against the position closes it and
      reverses: the raw signals with reversal (REVERSAL INTENDED); same-side signals while held are ignored.
    * The first profit stage (a close 20 % in profit moves the stop to the entry) is the house trail
      {"type": "lock_in", "gain": 0.20, "anchor": "close"} (the house reads minute closes, Pine the daily close).
      Mark trailing_stop. The later stages (stop at +30 % after a 50 % close, +60 % after an 80 % close) are a ratchet
      the house trail cannot express: not emitted, mark trailing_stop_pending (described in PORT_NOTES.md).
    * Stop module: portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their
      first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the first profit lock a house trail, the ratchet marked.
    2 generic: PASS, an ATR trail, an EMA and percentage gains.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482822_ut_bot_ema50_profit_lock"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "key": [1.1, 2.0],
    "atr_len": [200, 50],
}
DEFAULT_PARAMS = {"key": 1.1, "atr_len": 200, "ema_len": 50, "lock_gain": 0.20}


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


def _ut_trail(sr, nloss):
    m = len(sr)
    out = np.full(m, np.nan)
    prev = 0.0                              # nz(trail[1], 0)
    for i in range(m):
        s, nl = sr[i], nloss[i]
        if np.isnan(s) or np.isnan(nl):     # na in Pine; nz() reads it as 0 on the next bar
            prev = 0.0
            continue
        s1 = sr[i - 1] if i > 0 else np.nan
        if s > prev and (not np.isnan(s1)) and s1 > prev:
            t = max(prev, s - nl)
        elif s < prev and (not np.isnan(s1)) and s1 < prev:
            t = min(prev, s + nl)
        else:
            t = s - nl if s > prev else s + nl
        out[i] = t
        prev = t
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nloss = (p["key"] * _atr(bars_df, int(p["atr_len"]))).to_numpy()
    trail = pd.Series(_ut_trail(c.to_numpy(dtype=float), nloss), index=c.index)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    long_e = ((c > trail) & (c.shift(1) <= trail.shift(1)) & (c > ema)).astype(bool)
    short_e = ((c < trail) & (c.shift(1) >= trail.shift(1)) & (c < ema)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "lock_in", "gain": float(p["lock_gain"]), "anchor": "close"}}


def portfolio_kwargs(**params):
    return {}
