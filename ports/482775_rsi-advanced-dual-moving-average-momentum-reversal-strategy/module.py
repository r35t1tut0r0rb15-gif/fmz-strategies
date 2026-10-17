"""RSI 14 crossing up through 30 with the close at or below the lower Bollinger band (20, 2) goes long, crossing down
through 70 at or above the upper band goes short; closed at the middle band or the opposite RSI cross, 30-minute bars.
Port of FMZ strategy #482775 "高级双均线动量反转策略RSI与布林带协同交易系统-Advanced-Dual-Moving-Average-Momentum-Reversal-Strategy-RSI-and-Bollinger-Bands-Synergy-Trading-System" (RSI + Bollinger Bands Strategy).

FMZ source id: 482775

Source
    https://www.fmz.com/strategy/482775 (PineScript v5, FMZ last modified 2025-02-27 17:51:02).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 106-148), BB 20 / 2, RSI 14 (70 / 30)
    crossover(rsi, 30) and close <= lower -> entry long; crossunder(rsi, 70) and close >= upper -> entry short
    crossunder(rsi, 70) or close >= basis -> close long; crossover(rsi, 30) or close <= basis -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Closes are written after the entries: they act on the position held at the bar's start and never undo an entry
      on that bar (#430850). State machine; exits emitted only on going flat.
    * Entries reverse (REVERSAL INTENDED). Signal module, no stops. FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Bollinger bands and RSI levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity, quoted in original_sizing.txt.
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

NAME = "fmz_482775_rsi_cross_bb_extreme_reentry"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_mult": [2.0, 1.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    dev = p["bb_mult"] * c.rolling(n).std(ddof=0)
    rsi = _rsi(c, int(p["rsi_len"]))
    up_os = (rsi > p["os"]) & (rsi.shift(1) <= p["os"])
    dn_ob = (rsi < p["ob"]) & (rsi.shift(1) >= p["ob"])
    buy = (up_os & (c <= basis - dev)).to_numpy()
    sell = (dn_ob & (c >= basis + dev)).to_numpy()
    xl = (dn_ob | (c >= basis)).to_numpy()
    xs = (up_os | (c <= basis)).to_numpy()
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos = 0
    for i in range(m):
        start = pos
        if buy[i] and pos != 1:
            le[i], pos = True, 1
        if sell[i] and pos != -1:
            se[i], pos = True, -1
        if xl[i] and start == 1 and pos == 1:
            lx[i], pos = True, 0
        if xs[i] and start == -1 and pos == -1:
            sx[i], pos = True, 0
    idx = bars_df.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx), pd.Series(se, index=idx),
            pd.Series(sx, index=idx))


def portfolio_kwargs(**params):
    return {}
