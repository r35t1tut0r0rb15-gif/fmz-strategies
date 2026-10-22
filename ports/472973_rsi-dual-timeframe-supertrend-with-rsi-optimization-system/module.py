"""Close crossings of a 2-hour Supertrend line with a 15-minute RSI take-profit, 1-hour bars: the close crossing over the line goes long, crossing under goes short; a 30 % target from the fill, and a 15-minute RSI 5 at 95 or more (5 or less) closes the long (short); reversing.
Port of FMZ strategy #472973 "双时间周期超级趋势与RSI策略优化系统-Dual-Timeframe-Supertrend-with-RSI-Optimization-System" (Supertrend Strategy (2-hour Supertrend, 15-minute RSI)).

FMZ source id: 472973

Source
    https://www.fmz.com/strategy/472973 (PineScript v5, FMZ last modified 2024-11-25 17:27:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-171), Supertrend 3.42 / ATR 14 on request.security("120"); RSI 5 on request.security("15"); target 30 % of the average price
    crossover(close, st_120) -> (close Short) entry Long;  crossunder -> (close Long) entry Short
    long: exit(limit = avg x 1.3);  long and rsi15 >= 95 -> close Long;  short: exit(limit = avg x 0.7);  short and rsi15 <= 5 -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "120" request without lookahead is read as the last 2-hour bar completed by the chart bar's
      close (#440503) and the "15" request as the chart bar's last 15-minute bar (#436765), both built in
      precompute from the minutes (Pine's built-in supertrend on the 2-hour bars, RSI 5 on the 15-minute
      closes). The target comes from the average (fill) price: ported active from the fill bar (#440797)
      as the fixed fraction 0.30. The RSI closes act only on a position held into the bar; they are sent
      as exits that give way to an entry on the same bar. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 2-hour and 15-minute values from completed bars; the fill-price target as a fixed fraction.
    2 generic: PASS, higher-time-frame Supertrend crossings with an RSI exit.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_472973_close_cross_2h_supertrend_15m_rsi_exit_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [3.42, 2.0],
    "tp_pct": [0.30, 0.05],
}
DEFAULT_PARAMS = {"factor": 3.42, "tp_pct": 0.30, "atr_period": 14, "rsi_len": 5, "rsi_upper": 95, "rsi_lower": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): (direction -1 up / 1 down, line)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return dr, st


def _map(bars, src_index, values, minutes):
    """The value of the last `minutes` bar completed by each chart bar's close."""
    end_src = src_index.to_numpy().astype("datetime64[ns]") + np.timedelta64(minutes, "m")
    end_bar = bars.index.to_numpy().astype("datetime64[ns]") + np.timedelta64(60, "m")
    k = np.searchsorted(end_src, end_bar, side="right") - 1
    return np.where(k >= 0, np.asarray(values, dtype=float)[np.clip(k, 0, None)], np.nan)


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    bars = _resample(raw_1m_df, FREQ)
    b2 = _resample(raw_1m_df, "2h")
    _, st = _supertrend(b2["high"], b2["low"], b2["close"], float(p["factor"]), int(p["atr_period"]))
    bars["st_2h"] = _map(bars, b2.index, st, 120)
    c15 = raw_1m_df["close"].dropna().resample("15min", label="left", closed="left").last().dropna()
    bars["rsi_15"] = _map(bars, c15.index, _rsi(c15, int(p["rsi_len"])).to_numpy(), 15)
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c, st, r = bars_df["close"], bars_df["st_2h"], bars_df["rsi_15"]
    le = (c > st) & (c.shift(1) <= st.shift(1))
    se = (c < st) & (c.shift(1) >= st.shift(1))
    lx = (r >= float(p["rsi_upper"])) & ~le & ~se
    sx = (r <= float(p["rsi_lower"])) & ~le & ~se
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
