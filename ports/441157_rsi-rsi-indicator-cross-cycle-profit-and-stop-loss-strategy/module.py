"""RSI 4 dips at a 50-bar high above the weekly 26-week average, 2-day bars, long only: on the previous bar's close, the 21-bar high equal to the 50-bar high, the RSI 4 crossing under 30 and the close
above the weekly average go long; the previous close 3 ATR(50) above or 2 ATR under the fill closes.
Port of FMZ strategy #441157 "RSI指标跨周期交叉的止盈止损策略RSI-Indicator-Cross-Cycle-Profit-and-Stop-Loss-Strategy" (Swing Trading System RSI).

FMZ source id: 441157

Source
    https://www.fmz.com/strategy/441157 (PineScript v4, FMZ last modified 2024-02-06 11:43:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 153-184), source close[1]; weekly sma(close[1], 26); highs 21 / 50; RSI 4 (30); profit 3 ATR(50), stop 2 ATR(50)
    s = security("W", sma(close[1], 26));  long = highest(close[1], 21) == highest(close[1], 50) and crossunder(rsi(close[1], 4), 30) and close[1] > s -> entry
    close[1] > position_avg_price + 3 atr(50) -> close_all;  close[1] < position_avg_price - 2 atr(50) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-4 security("W") without lookahead is read as the last completed higher bar; its
      expression already reads close[1], so the value is the 26-week average of the closes two to 27
      completed weeks back. Weeks are broker weeks (Monday to Friday by broker-day label), built from the
      module's own 2-day bars (a block is counted in the week of its first day). The exits are bar-close
      tests of the previous close against the fill price plus / minus ATR(50) of the current bar, sent at
      the next open. Long only. No sizing code. Bars are blocks of 2 broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly values from completed weeks.
    2 generic: PASS, high check, RSI cross and ATR distance tests.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day and broker week (17:00 America/New_York, DST by the zone).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_441157_rsi4_dip_at_high_weekly_trend_atr_exits_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of 2 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_period": [4, 2],
    "rsi_thresh": [30, 20],
}
DEFAULT_PARAMS = {"rsi_period": 4, "rsi_thresh": 30, "long_period": 26, "short_days": 21, "long_days": 50,
                  "profit_target": 3, "stop_loss": 2, "atr_len": 50, "days": 2}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")   # the Monday of the broker week
    wk = c.groupby(week).last()
    sw = wk.shift(1).rolling(int(p["long_period"])).mean().shift(1)   # close[1] inside, last completed week
    s = pd.Series(sw.reindex(week).to_numpy(), index=c.index)
    src = c.shift(1)
    hi_ok = src.rolling(int(p["short_days"])).max() == src.rolling(int(p["long_days"])).max()
    r = _rsi(src, int(p["rsi_period"]))
    th = float(p["rsi_thresh"])
    go = (hi_ok & (r < th) & (r.shift(1) >= th) & (src > s)).to_numpy()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"])).to_numpy()
    sv = src.to_numpy(dtype=float)
    ov = bars_df["open"].to_numpy(dtype=float)
    pt, sl = float(p["profit_target"]), float(p["stop_loss"])
    m = len(sv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held, entry_i = 0, -1
    for i in range(m):
        if held == 0 and go[i] and i + 1 < m:
            le[i], held, entry_i = True, 1, i + 1
        elif held == 1 and i >= entry_i:
            fill = ov[entry_i]
            if sv[i] > fill + atr[i] * pt or sv[i] < fill - atr[i] * sl:
                lx[i], held = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
