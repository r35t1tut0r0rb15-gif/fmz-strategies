"""SuperTrend (ATR 10 x 3) up-trend with EMA 13 / 34 order, the EMA 100 side and ADX 14 over 25, broker days: EMA 13 above 34 with the close above the EMA 100 goes long, EMA 13 below 34 with the close below goes short (also in the SuperTrend up-trend, as written); the close crossing under (over) the SuperTrend line closes a long (short); reversing.
Port of FMZ strategy #477553 "Multi Moving Average Supertrend with Bollinger Breakout Trading Strategy" (CJ - Multi1).

FMZ source id: 477553

Source
    https://www.fmz.com/strategy/477553 (PineScript v6, FMZ last modified 2025-01-06 13:48:19).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 125-215), RSI 14 daily / weekly / monthly (plotted only); BB 20 / 2 (plotted only); EMA 13 / 34 / 100; SuperTrend ATR 10 x 3; DMI 14 / 14, ADX level 25
    dir == -1 and ema13 > ema34 and close > ema100 and adx > 25 -> entry Buy;  crossunder(close, supertrend) -> close Buy
    dir == -1 and ema13 < ema34 and close < ema100 and adx > 25 -> entry Short;  crossover(close, supertrend) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The short entry also needs direction -1 (Pine's up-trend), as written. The entries are states and
      repeat; a loop follows the call order: a repeat on the held side is ignored and a close on that bar
      still acts, and a close leaves a same-bar reversal standing (as #441963). The weekly and monthly RSI requests and the bands are
      plotted only. The SuperTrend is Pine's reference ta.supertrend. REVERSAL INTENDED. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, SuperTrend, EMA and ADX filters with SuperTrend-line closes.
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

NAME = "fmz_477553_supertrend_up_ema13_34_100_adx25_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_level": [25, 20],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"adx_level": 25, "factor": 3.0, "atr_l": 10, "adx_length": 14}


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


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
    e1, e2, e3 = (c.ewm(span=n, adjust=False).mean() for n in (13, 34, 100))
    line, d = _supertrend(bars_df, float(p["factor"]), int(p["atr_l"]))
    adx = _dmi(bars_df, int(p["adx_length"]))[2]
    base = (d == -1) & (adx > float(p["adx_level"]))
    le = base & (e1 > e2) & (c > e3)
    se = base & (e1 < e2) & (c < e3)
    lc = ((c < line) & (c.shift(1) >= line.shift(1))).to_numpy()
    sc = ((c > line) & (c.shift(1) <= line.shift(1))).to_numpy()
    lev, sev = le.to_numpy(), se.to_numpy()
    m = len(lc)
    LE, LX = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    SE, SX = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if lev[i] and pos != 1:
            LE[i], nxt = True, 1
        if sev[i] and pos != -1:
            SE[i], nxt = True, -1
        if pos == 1 and lc[i] and not SE[i]:
            LX[i], nxt = True, 0
        if pos == -1 and sc[i] and not LE[i]:
            SX[i], nxt = True, 0          # a repeat short signal on the held short is ignored; the close acts
    ix = bars_df.index
    return (pd.Series(LE, index=ix), pd.Series(LX, index=ix),
            pd.Series(SE, index=ix), pd.Series(SX, index=ix))


def portfolio_kwargs(**params):
    return {}
