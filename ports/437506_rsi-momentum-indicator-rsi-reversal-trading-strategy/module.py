"""RSI 7 breakouts with a rising ADX and a 3-hour SMMA trend, broker days: the RSI crossing over 68 while the ADX (from the day's last 3-hour bars) has risen three bars in a row above 15 and the SMMA 20 of those
3-hour closes is rising goes long; the RSI crossing under 28 with the ADX rising and the SMMA falling goes short; reversing.
Port of FMZ strategy #437506 "动量指标RSI捕捉反转交易策略Momentum-Indicator-RSI-Reversal-Trading-Strategy" (RSI scalping).

FMZ source id: 437506

Source
    https://www.fmz.com/strategy/437506 (PineScript v3, FMZ last modified 2024-01-03 12:09:48).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 142-193), custom resolution on: 180 minutes; ADX 14 / DI 14; RSI 7 (the length input is not used), 28 / 68; SMMA 20
    o / c / l / h = security(tickerid, "180", ...);  ADX from change(h) / -change(l) of those and security(tickerid, "180", tr);  smma of c (20)
    longCondition = crossover(rsi(close, 7), 68) and ADX rising 3 bars and > 15 and smma rising 3 bars;  shortCondition = crossunder(rsi, 28) and smma falling 3 bars and ADX rising

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 3-hour values requested from a daily chart are the day's LAST 3-hour bar (a lower time frame
      returns its last bar inside the chart bar, as #436765), 3-hour bars counted from the broker day's
      start (17:00 America/New_York); the ADX and the SMMA then run over the daily samples, as written.
      The RSI is hard-coded to 7 (the length input is unused). DI lines carry their last value where the
      true range is zero (fixnan). REVERSAL INTENDED. No sizing code. Daily bars are broker days, stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 3-hour values end with the daily bar.
    2 generic: PASS, RSI levels, ADX and SMMA directions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone), 3-hour bars counted from its start; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437506_rsi_breakout_adx_smma_3h"
FAMILY = "rsi_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "smma_len": [20, 40],
    "adx_len": [14, 21],
}
DEFAULT_PARAMS = {"smma_len": 20, "adx_len": 14, "di_len": 14, "rsi_len": 7, "over_sold": 28.0,
                  "over_bought": 68.0, "tf_minutes": 180}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _fixnan(x):
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    ny = df.index.tz_convert("America/New_York") + pd.Timedelta(hours=7)
    key = np.asarray((ny - ny.normalize()) // pd.Timedelta(minutes=int(p["tf_minutes"])))
    b3 = df.groupby([lab, key]).agg({"high": "max", "low": "min", "close": "last"})
    pc = b3["close"].shift(1)
    tr3 = pd.concat([b3["high"] - b3["low"], (b3["high"] - pc).abs(), (b3["low"] - pc).abs()],
                    axis=1).max(axis=1, skipna=False)
    last3 = pd.DataFrame({"h3": b3["high"], "l3": b3["low"], "c3": b3["close"], "tr3": tr3})
    day = last3.index.get_level_values(0)
    last3 = last3[~day.duplicated(keep="last")]           # the day's last 3-hour bar
    last3.index = last3.index.get_level_values(0)
    bars = bars.join(last3)
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _smma(x, n):
    v, sma = x.to_numpy(dtype=float), x.rolling(n).mean().to_numpy()
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        prev = out[i - 1] if i else np.nan
        out[i] = sma[i] if np.isnan(prev) else (prev * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    h3, l3, c3, tr3 = (bars_df[k] for k in ("h3", "l3", "c3", "tr3"))
    up = h3.diff()
    down = -l3.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=c.index).where(down.notna())
    dl, al = int(p["di_len"]), int(p["adx_len"])
    trr = _rma(tr3, dl)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = _fixnan(100 * _rma(plus_dm, dl) / trr)
        minus = _fixnan(100 * _rma(minus_dm, dl) / trr)
        s = plus + minus
        adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), al)
    sm = _smma(c3, int(p["smma_len"]))
    adx_up = (adx > adx.shift(1)) & (adx.shift(1) > adx.shift(2)) & (adx.shift(2) > adx.shift(3)) & (adx > 15)
    sm_dn = (sm < sm.shift(1)) & (sm.shift(1) < sm.shift(2)) & (sm.shift(2) < sm.shift(3))
    sm_up = (sm > sm.shift(1)) & (sm.shift(1) > sm.shift(2)) & (sm.shift(2) > sm.shift(3))
    r = _rsi(c, int(p["rsi_len"]))
    r1 = r.shift(1)
    ob, os_ = float(p["over_bought"]), float(p["over_sold"])
    lc = (r > ob) & (r1 <= ob) & adx_up & sm_up
    sc = (r < os_) & (r1 >= os_) & sm_dn & adx_up
    false = pd.Series(False, index=bars_df.index)
    return lc, false, sc, false.copy()


def portfolio_kwargs(**params):
    return {}
