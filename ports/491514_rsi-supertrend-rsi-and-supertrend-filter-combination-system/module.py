"""RSI 14 crossing up through 35 in a bullish band direction goes long, crossing down through 65 in a bearish one goes short, broker days; reversing (the per-bar 1.5 % / 1 % bracket is pending).
Port of FMZ strategy #491514 "RSI与SuperTrend过滤策略组合系统趋势确认下的动量反转交易框架-RSI-and-SuperTrend-Filter-Combination-System-Momentum-Reversal-Trading-Framework-with-Trend-Confirmation" (RSI + SuperTrend Filter Strategy (45m BTCUSDT)).

FMZ source id: 491514

Source
    https://www.fmz.com/strategy/491514 (PineScript v5, FMZ last modified 2025-04-21 16:31:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 157-238), RSI 14 / 65 / 35; band ATR 10 x 3 (unratcheted); TP 1.5 %, SL 1 % from the current close; 100 % of equity
    dir := close > hl2 - 3 atr ? 1 : close < hl2 + 3 atr ? -1 : dir[1]
    crossover(rsi, 35) and dir == 1 -> entry Long;  crossunder(rsi, 65) and dir == -1 -> entry Short;  every bar: exit(limit / stop from the current close)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The direction uses unratcheted bands, so it is 1 whenever the close is over hl2 - 3 ATR, as written. The
      exits are sent on every bar from that bar's close, so the bracket follows the price: not ported, mark
      trailing_stop_pending (as the C170-C175 readings); the opposite entry is the exit. An entry on the
      other side reverses (REVERSAL INTENDED). Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the re-sent bracket pending.
    2 generic: PASS, RSI threshold crossings with a band-direction filter.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_491514_rsi14_35_65_cross_band_direction_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsiOversold": [35, 30],
    "atrMult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"rsiOversold": 35, "atrMult": 3.0, "rsiPeriod": 14, "atrPeriod": 10}


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
    r = r.where(dn != 0, 100.0).where(up != 0, 0.0)
    return r.where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atrPeriod"])) * float(p["atrMult"])
    hl2 = (h + lo) / 2
    above = (c > hl2 - atr).to_numpy()
    below = (c < hl2 + atr).to_numpy()
    m = len(c)
    dv = np.ones(m)
    d = 1
    for i in range(m):
        if above[i]:
            d = 1
        elif below[i]:
            d = -1
        dv[i] = d
    dr = pd.Series(dv, index=c.index)
    r = _rsi(c, int(p["rsiPeriod"]))
    os_ = float(p["rsiOversold"])
    ob = 100 - os_
    le = (r > os_) & (r.shift(1) <= os_) & (dr == 1)
    se = (r < ob) & (r.shift(1) >= ob) & (dr == -1)
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
