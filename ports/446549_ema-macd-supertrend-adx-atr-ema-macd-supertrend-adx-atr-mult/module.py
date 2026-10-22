"""EMA 12 / 26 crossings with ADX, ATR and MACD-histogram filters, daily bars: a cross up with the ADX over 15, ATR(14) over half ATR(20) and the histogram positive goes long, the mirror goes short; the
close crossing under the SuperTrend (3, 10) closes a long, over it closes a short; reversing.
Port of FMZ strategy #446549 "EMA-MACD-SuperTrend-ADX-ATR多重指标交易信号策略-EMA-MACD-SuperTrend-ADX-ATR-Multi-Indicator-Trading-Signal-Strategy" (EMA-MACD-SuperTrend-ADX-ATR Strategy).

FMZ source id: 446549

Source
    https://www.fmz.com/strategy/446549 (PineScript v5, FMZ last modified 2024-03-29 15:41:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 106-198), EMA 12 / 26; MACD 12 / 26 / 9; ADX (script's double rma) > 15; ATR 14 > 0.5 ATR 20; SuperTrend 3 x 10; backtest 2020-2024; 70 % of equity, capital 1000
    crossover(ema12, ema26) and adx > 15 and atr14 > 0.5 atr20 and hist > 0 -> entry Buy;  crossunder(close, supertrend) -> close Buy
    crossunder(ema12, ema26) and adx > 15 and atr14 > 0.5 atr20 and hist < 0 -> entry Sell;  crossover(close, supertrend) -> close Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is the script's own: rma of the directional moves divided by rma(tr), smoothed again, as
      written. ta.supertrend's line is na on the first bar. The 2020-2024 backtest window is dropped
      (the data window decides). Calls run in order: a close acts only on a position held into the bar
      and not reversed by that bar's entry. REVERSAL INTENDED. The 70 % of equity size is sizing. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA crossings with trend, volatility and MACD filters, SuperTrend exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 70 % of equity size and capital stored.
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

NAME = "fmz_446549_ema12_26_cross_adx_atr_hist_supertrend_exit_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [15.0, 25.0],
    "factor": [3.0, 2.0],
}
DEFAULT_PARAMS = {"adx_min": 15.0, "factor": 3.0, "atr_length": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    trr = _rma(tr, 14)
    pdm = _rma((h - h.shift(1)).clip(lower=0), 14)
    mdm = _rma((lo.shift(1) - lo).clip(lower=0), 14)
    pdi = 100 * _rma(pdm / trr, 14)
    mdi = 100 * _rma(mdm / trr, 14)
    adx = 100 * _rma((pdi - mdi).abs() / (pdi + mdi), 14)
    vol = _rma(tr, 14) > 0.5 * _rma(tr, 20)
    e12 = c.ewm(span=12, adjust=False).mean()
    e26 = c.ewm(span=26, adjust=False).mean()
    macd = e12 - e26
    hist = macd - macd.ewm(span=9, adjust=False).mean()
    _, st = _supertrend(h, lo, c, float(p["factor"]), int(p["atr_length"]))
    st[0] = np.nan                                    # supertrend := barstate.isfirst ? na : supertrend
    st = pd.Series(st, index=c.index)
    ok = (adx > float(p["adx_min"])) & vol
    lc = ((e12 > e26) & (e12.shift(1) <= e26.shift(1)) & ok & (hist > 0)).to_numpy()
    sc = ((e12 < e26) & (e12.shift(1) >= e26.shift(1)) & ok & (hist < 0)).to_numpy()
    xl = ((c < st) & (pc >= st.shift(1))).to_numpy()
    xs = ((c > st) & (pc <= st.shift(1))).to_numpy()
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if lc[i] and new != 1:
            le[i], new = True, 1
        if xl[i] and pos == 1 and new == 1:          # a close acts only on a held, non-reversed long
            lx[i], new = True, 0
        if sc[i] and new != -1:
            se[i], lx[i], le[i], new = True, False, False, -1
        if xs[i] and pos == -1 and new == -1:
            sx[i], new = True, 0
        pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
