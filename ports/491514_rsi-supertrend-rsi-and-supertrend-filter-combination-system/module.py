"""RSI 35 / 65 turns filtered by a simplified SuperTrend direction, with a percentage bracket, broker days: RSI 14
crossing up through 35 while the direction is up goes long; RSI crossing down through 65 while it is down goes short;
each trade has a 1 % stop and a 1.5 % target.
Port of FMZ strategy #491514 "RSI与SuperTrend过滤策略组合系统趋势确认下的动量反转交易框架-RSI-and-SuperTrend-Filter-Combination-System-Momentum-Reversal-Trading-Framework-with-Trend-Confirmation" (RSI + SuperTrend Filter Strategy (45m BTCUSDT)).

FMZ source id: 491514

Source
    https://www.fmz.com/strategy/491514 (PineScript v5, FMZ last modified 2025-04-21 16:31:17).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 161-197), RSI 14 (35 / 65), ATR 10 x 3, TP 1.5 %, SL 1 %
    superDir = close > hl2 - 3 ATR ? 1 : close < hl2 + 3 ATR ? -1 : superDir[1]   (as written: no band ratchet)
    long = crossover(rsi, 35) and superDir == 1;  short = crossunder(rsi, 65) and superDir == -1
    every bar: exit(limit = close x (1 +- 1.5 %), stop = close x (1 -+ 1 %)) for each side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The direction is the source's own two-band test, not the ratcheting ta.supertrend; as written it is -1 only on
      a close at or below hl2 - 3 ATR.
    * The bracket is re-issued at every bar's close (a moving level): mark trailing_stop_pending. The port fixes it
      at the signal bar: sl_stop 1 %, tp_stop 1.5 % of the fill price (scalars).
    * Entries reverse (REVERSAL INTENDED); a long and a short cannot fall on one bar (RSI cannot cross up through 35
      and down through 65 together).
    * The title's "45m BTCUSDT" is a label; FREQ = "1D" from the backtest header (broker days, 17:00
      America/New_York, stamped with their first minute): coarse_bar_stop. Stop module: portfolio_kwargs {} (D4).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (mark).
    2 generic: PASS, oscillator levels, ATR bands and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491514_rsi_turn_supertrend_dir_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_oversold": [35, 30],
    "atr_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_overbought": 65, "rsi_oversold": 35, "tp_pct": 1.5, "sl_pct": 1.0,
                  "atr_len": 10, "atr_mult": 3.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    rsi = _rsi(c, int(p["rsi_len"]))
    atr = _atr(bars_df, int(p["atr_len"]))
    hl2 = (h + lo) / 2
    up_b, lo_b = (hl2 + p["atr_mult"] * atr).to_numpy(), (hl2 - p["atr_mult"] * atr).to_numpy()
    cv = c.to_numpy(dtype=float)
    d = np.ones(len(cv), dtype=np.int8)
    cur = 1                                        # var int superDir = 1
    for i in range(len(cv)):
        if cv[i] > lo_b[i]:
            cur = 1
        elif cv[i] < up_b[i]:
            cur = -1
        d[i] = cur                                 # na bands keep the previous value
    long_e = ((rsi > p["rsi_oversold"]) & (rsi.shift(1) <= p["rsi_oversold"]) & (d == 1)).astype(bool)
    short_e = ((rsi < p["rsi_overbought"]) & (rsi.shift(1) >= p["rsi_overbought"]) & (d == -1)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
