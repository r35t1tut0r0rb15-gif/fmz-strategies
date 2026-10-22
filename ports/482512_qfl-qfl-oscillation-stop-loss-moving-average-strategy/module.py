"""QFL base breaks, broker days, long only: a low more than 0.5 % under the previous 50-bar lowest close (once any panic-range bar has been seen) buys, at most once per 5-bar cooldown; a close at least 1 % over the entry price and over the rebound level (base + 0.8 x the 3-bar range) closes.
Port of FMZ strategy #482512 "QFL震荡条件止损均线策略-QFL-Oscillation-Stop-Loss-Moving-Average-Strategy" (Jackson Quickfingersluc (QFL) Strategy).

FMZ source id: 482512

Source
    https://www.fmz.com/strategy/482512 (PineScript v6, FMZ last modified 2025-02-18 18:18:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 88-217), base = lowest(close, 50)[1] x 1; rebound = base + 0.8 x 3-bar range; ATR 14 x 1.2 panic test; panic 0.5 % under base; exit 1 % over the avg price; cooldown 5 bars; TP option avg_price
    panic movement (var, set once): any of the last 1..4 bars' ranges or average ranges over 1.2 atr
    low < base x (1 - 0.005) and panic movement and bar_index - lastEntryBar > 5 -> entry Buy (lastEntryBar := bar_index)
    (close - avg) / avg >= 0.01 and close > rebound -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * The panic-movement flag is a var that is set once and never cleared, so after the first wide bar
      only the base break and the cooldown gate the entries, as written. The cooldown restarts on every
      qualifying bar, also while a long is held (the entry is then ignored: one position). The take-profit
      test uses the entry price and acts only on a long held into the bar: a loop. The other take-profit
      options are not the default and are not ported. Long only. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exit on a percent gain over the entry price.
    2 generic: PASS, base-break dip buying with a rebound exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482512_qfl_base50_panic_break_cooldown5_rebound_exit_long"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "look_back_period": [50, 100],
    "exit_profit_threshold": [0.01, 0.03],
}
DEFAULT_PARAMS = {"look_back_period": 50, "exit_profit_threshold": 0.01, "base_mult": 1.0, "rebound_mult": 0.8,
                  "atr_period": 14, "atr_mult": 1.2, "panic_pct": 0.005, "range_bars": 3, "cooldown_bars": 5}


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


def _atr(b, n):
    h, lo, pc = b["high"], b["low"], b["close"].shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    base = c.rolling(int(p["look_back_period"])).min().shift(1) * float(p["base_mult"])
    nr = int(p["range_bars"])
    rebound = float(p["rebound_mult"]) * (h.rolling(nr).max() - lo.rolling(nr).min()) + base
    lim = float(p["atr_mult"]) * _atr(bars_df, int(p["atr_period"]))
    wide = pd.Series(False, index=c.index)
    for j in range(1, nr + 2):
        span = (h.rolling(j).max() - lo.rolling(j).min()) / j > lim
        one = (h.shift(j - 1) - lo.shift(j - 1)) > lim
        wide = wide | span | one
    panic_seen = np.maximum.accumulate(wide.to_numpy())             # var flag, never cleared
    panic = ((lo < base * (1 - float(p["panic_pct"]))).to_numpy()) & panic_seen
    rb = (c > rebound).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    thr, cd = float(p["exit_profit_threshold"]), int(p["cooldown_bars"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg, last = 0, 0, np.nan, -1
    for i in range(m):
        if pend == 1:
            pos, avg = 1, ov[i]
        elif pend == 2:
            pos, avg = 0, np.nan
        pend = 0
        if panic[i] and (last < 0 or i - last > cd):
            last = i                              # restarts also when the entry is ignored
            if pos == 0:
                le[i], pend = True, 1
        if pos == 1 and (cv[i] - avg) / avg >= thr and rb[i]:
            lx[i], pend = True, 2
    idx = c.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
