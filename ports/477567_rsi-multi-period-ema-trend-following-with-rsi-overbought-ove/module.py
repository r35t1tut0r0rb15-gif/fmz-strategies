"""EMA 20 / 50 trend states with the close beyond the EMA 20 and RSI 14 short of the extreme, broker days: up-trend above with RSI under 70 goes long, down-trend below with RSI over 30 goes short; every position is closed once it has been held 5 bars; reversing.
Port of FMZ strategy #477567 "多周期均线趋势跟踪结合RSI超买超卖动态优化策略-Multi-Period-EMA-Trend-Following-with-RSI-Overbought-Oversold-Dynamic-Optimization-Strategy" (High Win Rate BTC Strategy).

FMZ source id: 477567

Source
    https://www.fmz.com/strategy/477567 (PineScript v5, FMZ last modified 2025-01-06 14:10:46).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-139), EMA 20 / 50; RSI 14, 70 / 30; ATR 14 over 1.0; hold 5 bars
    in a position -> holdCount += 1, else 0;  uptrend and close > ema20 and rsi < 70 and atr > 1 -> entry Long;  downtrend and close < ema20 and rsi > 30 and atr > 1 -> entry Short;  holdCount >= 5 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * A loop counts the bars a position is held (a reversal does not reset the count, as written, since
      the position stays open) and closes all at the next open from the fifth. The entries are states
      and repeat: a repeat on the held side is ignored, a close on that bar ends the trade (as #472251),
      and a reversal on the close bar stands. The ATR threshold of 1.0 is a price amount, ported as a
      fraction of 42000 of the close (2.381e-05). REVERSAL INTENDED. No sizing code. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend states with an RSI filter and a 5-bar hold.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477567_ema20_50_trend_rsi_filter_hold5_reversal"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "hold_bars": [5, 10],
    "ema_long": [50, 100],
}
DEFAULT_PARAMS = {"hold_bars": 5, "ema_long": 50, "ema_short": 20, "rsi_length": 14, "atr_length": 14,
                  "atr_frac": 2.381e-05}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    vol_ok = _atr(bars_df, p["atr_length"]) > float(p["atr_frac"]) * c
    lc = ((es > el) & (c > es) & (r < 70) & vol_ok).to_numpy()
    sc = ((es < el) & (c < es) & (r > 30) & vol_ok).to_numpy()
    hold = int(p["hold_bars"])
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, cnt = 0, 0, 0
    for i in range(m):
        pos = nxt
        cnt = cnt + 1 if pos != 0 else 0
        if lc[i] and pos != 1:
            le[i], nxt = True, 1
        if sc[i] and pos != -1:
            se[i], nxt = True, -1
        if cnt >= hold:
            if pos == 1 and not se[i]:
                lx[i], nxt = True, 0
            elif pos == -1 and not le[i]:
                sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
