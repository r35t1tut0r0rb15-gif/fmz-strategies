"""Broker days, long only: the first day on which at least 2 of 9 bullish conditions hold (golden cross, rising RSI under 40, MACD cross-up, stochastic cross-up from under 30, a green close near a 260-bar Fibonacci level, SAR under the price, a rising ADX over 15 with DI+ over DI-, a green high-volume day, a bullish reversal candle) goes long; nothing ever closes it (as written).
Port of FMZ strategy #485291 "Multi Dimensional Technical Indicator Cross Confirmation Buy Signal Optimization Strategy" (My Buy Signal Strategy).

FMZ source id: 485291

Source
    https://www.fmz.com/strategy/485291 (PineScript v5, FMZ last modified 2025-03-07 14:31:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 154-219), SMA 50 / 200; RSI 14; MACD 12 / 26 / 9; stoch 14 / 3 / 3 (arguments as written); Fibonacci 260 bars +-1 %; SAR 0.02 / 0.02 / 0.2; DMI 14; volume SMA 20; min_conditions 2
    count = cond1 .. cond10 (no cond4);  count >= 2 -> entry Buy;  no exit
    stoch_raw = ta.stoch(high, low, close, 14)  (source = high, high = low, low = close);  adx_val = rma(100 x |DI+ - DI-| / (DI+ + DI-), 14)

Interpretation choices (Pine rules in SURVEY_README.md)
    * There is no exit of any kind: the first qualifying day opens a long held to the end of the data,
      as written (as #458234); with only 2 of 9 conditions needed that is usually one of the first days
      with full history. ta.stoch is called with its arguments shifted (source = high, high series = low,
      low series = close), as written. The SAR is Pine's ta.sar; the ADX is re-smoothed from ta.dmi's DI
      lines. Long only. No sizing code. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, a nine-condition bullish vote.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per broker day) against its SMA 20 in condition 9; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_485291_nine_condition_vote_buy_no_exit_long_only"
FAMILY = "indicator_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "min_conditions": [2, 4],
    "fib_len": [260, 120],
}
DEFAULT_PARAMS = {"min_conditions": 2, "fib_len": 260}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _fixnan(x):
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi_di(h, lo, c, n):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    return _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def _xo(a, b):
    return (a > b) & (a.shift(1) <= b.shift(1))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    c1 = _xo(c.rolling(50).mean(), c.rolling(200).mean())
    r = _rsi(c, 14)
    c2 = (r < 40) & (r > r.shift(1))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    c3 = _xo(macd, macd.ewm(span=9, adjust=False).mean())
    ll, hh = c.rolling(14).min(), lo.rolling(14).max()          # ta.stoch(high, low, close, 14) as written
    k = (100 * (h - ll) / (hh - ll).where(hh != ll)).rolling(3).mean()
    d = k.rolling(3).mean()
    c5 = _xo(k, d) & (k.shift(1) < 30)
    n = int(p["fib_len"])
    sl_, sh_ = lo.rolling(n).min(), h.rolling(n).max()
    near = pd.Series(False, index=c.index)
    for f in (0.382, 0.5, 0.618):
        lvl = sh_ - f * (sh_ - sl_)
        near |= (c >= lvl - 0.01 * c) & (c <= lvl + 0.01 * c)
    c6 = near & (c > o)
    psar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float), 0.02, 0.02, 0.2),
                     index=c.index)
    c7 = psar < c
    dip, dim = _dmi_di(h, lo, c, 14)
    adx = _rma(100 * (dip - dim).abs() / (dip + dim), 14)
    c8 = (adx > 15) & (adx > adx.shift(1)) & (dip > dim)
    c9 = (c > o) & (v > v.rolling(20).mean())
    body = c - o
    hamm = (c > o) & ((h - c) <= body) & ((o - lo) >= 1.5 * body)
    inv = (c > o) & ((h - c) >= 1.5 * body) & ((o - lo) <= body)
    mstar = ((c.shift(2) < o.shift(2)) & ((c.shift(1) - o.shift(1)).abs() < (o.shift(2) - c.shift(2)) * 0.75)
             & (c > o) & (c > c.shift(1)) & (o.shift(1) < c.shift(2)))
    c10 = hamm | inv | mstar
    count = sum(x.astype(int) for x in (c1, c2, c3, c5, c6, c7, c8, c9, c10))
    entry = count >= int(p["min_conditions"])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return entry.astype(bool), false, false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
