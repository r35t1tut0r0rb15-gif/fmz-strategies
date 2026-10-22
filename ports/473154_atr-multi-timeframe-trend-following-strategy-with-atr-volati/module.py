"""EMA 9 / 21 crossings with RSI and daily-EMA confirmation, daily bars: the cross up with the RSI under 70 and the close over the EMA 21 goes long, the mirror goes short; a held position closes when the close crosses its ratcheting 1.5 ATR stop line; reversing.
Port of FMZ strategy #473154 "多周期趋势跟踪与ATR波动率管理策略-Multi-Timeframe-Trend-Following-Strategy-with-ATR-Volatility-Management" (Trend Following with ATR and MTF Confirmation).

FMZ source id: 473154

Source
    https://www.fmz.com/strategy/473154 (PineScript v5, FMZ last modified 2024-11-27 16:39:41).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 96-176), EMA 9 / 21; RSI 14, 70 / 30; ATR 14: trailing stop line 1.5 x (one var for both sides, never reset), target close + 2 ATR (never reachable); request.security("D") EMA 21 (the chart itself)
    held long: trail = max(trail, close - 1.5 atr), exit(stop = trail, limit = close + 2 atr, when = close <= trail or close >= close + 2 atr)
    held short: trail = min(trail, close + 1.5 atr), exit(..., when = close >= trail or close <= close - 2 atr)
    crossover and rsi < 70 and close > ema21_D -> entry Long;  crossunder and rsi > 30 and close < ema21_D -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent only when its close test holds, with the stop at or through the market, so it
      fills at the next open: a bar-close exit. The target test compares the close with itself plus 2
      ATR and never holds. The trail is one var shared by both sides and never reset between trades, as
      written (a new trade starts from the old line). The exits come before the entries in the script;
      an entry on the same bar takes the place of the close (#437773). The "D" request is the chart's own
      EMA 21. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trailing line as a close test.
    2 generic: PASS, EMA crossings with filters and an ATR trailing line.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND472951 (2 members, best partner #472951, Jaccard 0.665); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_473154_ema9_21_cross_rsi_filter_shared_atr_trail_close_test_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "fast": [9, 5],
    "slow": [21, 50],
    "atr_mult": [1.5, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "atr_mult": 1.5, "rsi_len": 14, "atr_len": 14}


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
    a, b = c.ewm(span=int(p["fast"]), adjust=False).mean(), c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_len"]))
    lc = ((a > b) & (a.shift(1) <= b.shift(1)) & (r < 70) & (c > b)).to_numpy()
    sc = ((a < b) & (a.shift(1) >= b.shift(1)) & (r > 30) & (c < b)).to_numpy()
    dist = (float(p["atr_mult"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, trail = 0, np.nan
    for i in range(m):
        cur = pos
        if pos == 1:
            cand = cv[i] - dist[i]
            trail = cand if np.isnan(trail) else max(trail, cand)
            if cv[i] <= trail:
                cur = 0
        elif pos == -1:
            cand = cv[i] + dist[i]
            trail = cand if np.isnan(trail) else min(trail, cand)
            if cv[i] >= trail:
                cur = 0
        if lc[i]:
            cur = 1
        if sc[i]:
            cur = -1
        if cur == 1 and pos != 1:
            le[i] = True
        elif cur == -1 and pos != -1:
            se[i] = True
        elif cur == 0 and pos == 1:
            lx[i] = True
        elif cur == 0 and pos == -1:
            sx[i] = True
        pos = cur
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
