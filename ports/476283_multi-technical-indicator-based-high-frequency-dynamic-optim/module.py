"""EMA 9 / 21 crossings with ADX 14 over 20 and RSI 14 short of the extreme, broker days, entries only from flat: the cross up with RSI under 70 goes long, the cross down with RSI over 30 goes short; RSI over 70 closes a long, under 30 a short.
Port of FMZ strategy #476283 "Multi Technical Indicator Based High Frequency Dynamic Optimization Strategy" (Scalping BTC Ottimizzato - Grafica Chiara).

FMZ source id: 476283

Source
    https://www.fmz.com/strategy/476283 (PineScript v5, FMZ last modified 2024-12-27 15:58:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 82-192), EMA 9 / 21; RSI 14, 70 / 30; ATR 14 x 1.5 / 2.0 bracket from strategy.position_avg_price; ADX 14 / 14 over 20; 10 % of equity
    crossover(ema9, ema21) and rsi < 70 and adx > 20 and flat -> entry Long, exit(stop = avg - 1.5 atr, limit = avg + 2 atr);  crossunder and rsi > 30 and adx > 20 and flat -> entry Short, exit(mirror)
    rsi > 70 and long -> close Long;  rsi < 30 and short -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent only on a signal bar taken from flat, from strategy.position_avg_price, which is
      na then: the stop and limit are na and no bracket is ever placed (as #473147, "na from flat").
      Entries only from flat (strategy.position_size at the bar's close); a close acts only on a position
      held into the bar. Opposite entries cannot occur (entries only from flat). The 10 % of equity size
      is sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the na bracket places nothing, as written.
    2 generic: PASS, EMA crossings with ADX and RSI filters, RSI extreme closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported; the ATR bracket inputs stored (never placed).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_476283_ema9_21_cross_adx20_rsi_extreme_close_flat_only"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_threshold": [20, 25],
    "fast": [9, 5],
}
DEFAULT_PARAMS = {"adx_threshold": 20, "fast": 9, "slow": 21, "rsi_length": 14, "adx_length": 14}


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
    return 100 - 100 / (1 + up / dn)


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    strong = adx > float(p["adx_threshold"])
    lc = ((f > s) & (f.shift(1) <= s.shift(1)) & (r < 70) & strong).to_numpy()
    sc = ((f < s) & (f.shift(1) >= s.shift(1)) & (r > 30) & strong).to_numpy()
    ob, os_ = (r > 70).to_numpy(), (r < 30).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if pos == 0 and lc[i]:
            le[i], nxt = True, 1
        elif pos == 0 and sc[i]:
            se[i], nxt = True, -1
        if pos == 1 and ob[i]:
            lx[i], nxt = True, 0
        elif pos == -1 and os_[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
