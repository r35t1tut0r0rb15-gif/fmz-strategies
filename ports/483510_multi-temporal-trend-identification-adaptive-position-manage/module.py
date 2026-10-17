"""Close crossing the Supertrend (10, 3) filtered by DEMA 100, with reversals, 5-minute bars: the close crossing above
the Supertrend line with the close above DEMA 100 goes long (closing a short); crossing below with the close below DEMA
100 goes short (closing a long); a cross against the DEMA filter only closes the opposite position.
Port of FMZ strategy #483510 "多重时序趋势甄别型自适应动态调仓策略-Multi-Temporal-Trend-Identification-Adaptive-Position-Management-Strategy" (Supertrend with DEMA Strategy (Reversal Enabled)).

FMZ source id: 483510

Source
    https://www.fmz.com/strategy/483510 (PineScript v6, FMZ last modified 2025-02-27 16:49:07).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 109-182), ATR 10, factor 3, DEMA 100, allow long / short
    trendUp = crossover(close, supertrend); trendDown = crossunder(close, supertrend)
    longSignal = trendUp and close > dema: close a short, enter long (if allowed); shortSignal mirrored
    trendUp and not longSignal and short: close the short (mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.supertrend as TradingView documents it (pine_supertrend: hl2 +- factor x ATR, bands ratcheted while the prior
      close stays inside, direction from the prior line); the line is na on the first bar, as written.
    * With a short allowed off (allow_short False) a short signal only closes the long; the switch is a GRID variant.
      allowLong stays True (the source's default).
    * Entries reverse (REVERSAL INTENDED); an exit is never emitted on a bar with the opposite entry. No stops.
      FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Supertrend (ATR bands) and a DEMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
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

NAME = "fmz_483510_supertrend_cross_dema_filter_reversal"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [3.0, 2.0],
    "allow_short": [True, False],
}
DEFAULT_PARAMS = {"atr_len": 10, "factor": 3.0, "dema_len": 100, "allow_short": True}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _supertrend_pine(bars_df, factor, n):
    """ta.supertrend (pine_supertrend): returns the line; nan comparisons are false, as in Pine."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    atr = _atr(bars_df, n).to_numpy(dtype=float)
    src = (h + lo) / 2
    m = len(c)
    st = np.full(m, np.nan)
    prev_u = prev_l = prev_st = np.nan
    for i in range(m):
        up, lw = src[i] + factor * atr[i], src[i] - factor * atr[i]
        pl = 0.0 if np.isnan(prev_l) else prev_l               # nz(lowerBand[1])
        pu = 0.0 if np.isnan(prev_u) else prev_u
        pc = c[i - 1] if i > 0 else np.nan
        lw = lw if (lw > pl or pc < pl) else pl
        up = up if (up < pu or pc > pu) else pu
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif prev_st == pu:
            d = -1 if c[i] > up else 1
        else:
            d = 1 if c[i] < lw else -1
        st[i] = lw if d == -1 else up
        prev_u, prev_l, prev_st = up, lw, st[i]
    st[0] = np.nan                                           # barstate.isfirst ? na
    return pd.Series(st, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    st = _supertrend_pine(bars_df, float(p["factor"]), int(p["atr_len"]))
    n = int(p["dema_len"])
    e1 = c.ewm(span=n, adjust=False).mean()
    dema = 2 * e1 - e1.ewm(span=n, adjust=False).mean()
    t_up = ((c > st) & (c.shift(1) <= st.shift(1))).astype(bool)
    t_dn = ((c < st) & (c.shift(1) >= st.shift(1))).astype(bool)
    long_e = (t_up & (c > dema)).astype(bool)
    short_e = (t_dn & (c < dema)).astype(bool) if p["allow_short"] else pd.Series(False, index=c.index)
    short_x = (t_up & ~long_e).astype(bool)
    long_x = (t_dn & ~short_e).astype(bool)
    return long_e, long_x, short_e, short_x


def portfolio_kwargs(**params):
    return {}
