"""CMO signal-line cross confirmed by momentum and the SuperTrend side: CMO crossing above its
SMA with rising positive momentum above an up-trend SuperTrend goes long; the mirror goes short.
Port of FMZ strategy #363001 "Trading the Equity Curve Position Sizing Example".

Source
    https://www.fmz.com/strategy/363001 (PineScript v5, FMZ last modified 2022-05-13 22:30:27).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 111-143), CMO 9 / signal 10, SuperTrend 10 x 3, mom 12
    mom0 = mom(close, 12); mom1 = mom(mom0, 1); [st, dir] = supertrend(3, 10)
    long  = crossover(cmo, sma(cmo, 10)) and mom0 > 0 and mom1 > 0 and close > (dir < 0 ? st : na)
    short = crossunder(cmo, sma(cmo, 10)) and mom0 < 0 and mom1 < 0 and close < (dir < 0 ? na : st)
    long -> entry long; short -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trading the equity curve" part only changes the order quantity (equity SMAs);
      it is sizing (criterion 4) -> original_sizing.txt. With useTEC on (default), the Adj*
      entries are the active ones; their rules equal the Def* ones.
    * ta.cmo = 100 * (sum of gains - sum of losses) / (sum of gains + sum of losses) over 9.
    * strategy.entry reverses: REVERSAL INTENDED (portfolio_kwargs {}). The long line is
      evaluated first.
    * FREQ = "15min" from the backtest header.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_363001_cmo_cross_mom_supertrend"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "cmo_len": [9, 14],
    "st_factor": [2.0, 3.0],
    "mom_len": [12, 24],
}
DEFAULT_PARAMS = {"cmo_len": 9, "cmo_signal": 10, "st_atr": 10, "st_factor": 3.0, "mom_len": 12}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr_pine(bars, n):
    """ta.atr: Wilder RMA of the true range; the first bar's range is high - low (ta.tr(true))."""
    prev_close = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"],
                    (bars["high"] - prev_close).abs(),
                    (bars["low"] - prev_close).abs()], axis=1).max(axis=1)
    return _rma(tr, n)


def _supertrend(bars, factor, atr_period):
    """ta.supertrend(factor, atrPeriod) as in Pine v5: returns (supertrend, direction);
    direction < 0 is an up-trend."""
    atr = _atr_pine(bars, atr_period).to_numpy()
    h, lo, c = (bars[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    hl2 = (h + lo) / 2
    m = len(c)
    st, dirn = np.full(m, np.nan), np.full(m, np.nan)
    lower_prev = upper_prev = 0.0      # nz(...[1])
    st_prev = np.nan
    for i in range(m):
        lower, upper = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        if i > 0:
            if not (lower > lower_prev or c[i - 1] < lower_prev):
                lower = lower_prev
            if not (upper < upper_prev or c[i - 1] > upper_prev):
                upper = upper_prev
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif st_prev == upper_prev:
            d = -1 if c[i] > upper else 1
        else:
            d = 1 if c[i] < lower else -1
        st[i] = lower if d == -1 else upper
        dirn[i] = d
        lower_prev = 0.0 if np.isnan(lower) else lower
        upper_prev = 0.0 if np.isnan(upper) else upper
        st_prev = st[i]
    return pd.Series(st, index=bars.index), pd.Series(dirn, index=bars.index)


def _always_in(long_sig, short_sig, index, short_first=False):
    """Stop-and-reverse from two condition arrays (first matching line in source order wins)."""
    m = len(long_sig)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        first, second = ((short_sig, -1), (long_sig, 1)) if short_first else ((long_sig, 1), (short_sig, -1))
        for sig, side in (first, second):
            if sig[i]:
                if pos != side:
                    (le if side == 1 else se)[i] = True
                    pos = side
                break
    false = pd.Series(False, index=index)
    return pd.Series(le, index=index), false.copy(), pd.Series(se, index=index), false.copy()


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    n = int(p["cmo_len"])
    su, sd = d.clip(lower=0).rolling(n).sum(), (-d).clip(lower=0).rolling(n).sum()
    cmo = 100 * (su - sd) / (su + sd)
    sig = cmo.rolling(int(p["cmo_signal"])).mean()
    x_up = (cmo > sig) & (cmo.shift(1) <= sig.shift(1))
    x_dn = (cmo < sig) & (cmo.shift(1) >= sig.shift(1))
    mom0 = c - c.shift(int(p["mom_len"]))
    mom1 = mom0 - mom0.shift(1)
    st, dirn = _supertrend(bars_df, float(p["st_factor"]), int(p["st_atr"]))
    up_line, dn_line = st.where(dirn < 0), st.where(~(dirn < 0) & dirn.notna())
    long_ = (x_up & (mom0 > 0) & (mom1 > 0) & (c > up_line)).to_numpy()
    short = (x_dn & (mom0 < 0) & (mom1 < 0) & (c < dn_line)).to_numpy()
    return _always_in(long_, short, bars_df.index)


def portfolio_kwargs(**params):
    return {}
