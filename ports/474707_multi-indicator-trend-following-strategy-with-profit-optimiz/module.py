"""Parabolic SAR breaks in an SMA 50 uptrend with +DI over -DI, daily bars, long only: a close crossing over the SAR buys (when the strategy's own position flag is off) and stores the close; a close at or over that price + 3 % sells at the next open. A MACD cross down also clears the flag and rests a sell limit at the target, which is not ported (pending).
Port of FMZ strategy #474707 "Multi Indicator Trend Following Strategy with Profit Optimization" (Swing Trading Strategy with DMI).

FMZ source id: 474707

Source
    https://www.fmz.com/strategy/474707 (PineScript v5, FMZ last modified 2024-12-11 17:22:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-186), SAR 0.02 / 0.02 / 0.2; SMA 50; DMI 14 / 14; MACD 12 / 26 / 9; target 3 %
    crossover(close, sar) and close > sma50 and +DI > -DI and not inPosition -> buyPrice := close, inPosition := true, entry Buy;  inPosition and (close >= buyPrice x 1.03 or crossunder(macd, signal)) -> inPosition := false, exit(limit = buyPrice x 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flag inPosition is the script's own, kept in a loop. When the sell fires on a close at or
      over the target, the limit sits under the market and fills at the next open: a close exit. When it
      fires on the MACD cross under the target, the limit rests until the price reaches it, an exit
      armed only by the exit condition: not ported (as #437800, mark trailing_stop_pending), so that
      trade waits for a later flag cycle. A new buy signal while still long only re-stores the price (the
      entry is ignored). Long only. No sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SAR breaks with SMA / DMI filters and a target close; resting limit described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_474707_sar_break_sma50_dmi_target_close_long"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "sma_len": [50, 100],
    "target_pct": [3.0, 6.0],
}
DEFAULT_PARAMS = {"sma_len": 50, "target_pct": 3.0}


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


def _sar_pine(bars, start, inc, maximum):
    """ta.sar as TradingView documents it (pine_sar): starts on bar 1, direction from close vs
    the previous close; value capped by the previous two bars' lows (highs)."""
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    out = np.full(m, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, m):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below and h[i] > max_min:
                max_min, acc = h[i], min(acc + inc, maximum)
            elif (not below) and lo[i] < max_min:
                max_min, acc = lo[i], min(acc + inc, maximum)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return pd.Series(out, index=bars.index)


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
    sar = _sar_pine(bars_df, 0.02, 0.02, 0.2)
    pdi, mdi, _ = _dmi(bars_df, 14)
    buy = ((c > sar) & (c.shift(1) <= sar.shift(1)) & (c > c.rolling(int(p["sma_len"])).mean()) & (pdi > mdi)).to_numpy()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    mx = ((macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    cv = c.to_numpy(dtype=float)
    k = 1 + float(p["target_pct"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    flag, bp = False, np.nan
    for i in range(m):
        if buy[i] and not flag:
            bp, flag, le[i] = cv[i], True, True
        if flag and (cv[i] >= bp * k or mx[i]):
            flag = False
            if cv[i] >= bp * k:
                lx[i] = True                     # the limit is under the market: filled at the next open
    lx &= ~le
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
