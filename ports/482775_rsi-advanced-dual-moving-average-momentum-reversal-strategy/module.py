"""RSI 14 leaving its extremes at a Bollinger band (20, 2), 30-minute bars: RSI crossing back over 30 with the close at or under the lower band goes long, crossing back under 70 at or over the upper band goes short; a long closes at the basis or when RSI crosses under 70, a short mirrors it.
Port of FMZ strategy #482775 "高级双均线动量反转策略RSI与布林带协同交易系统-Advanced-Dual-Moving-Average-Momentum-Reversal-Strategy-RSI-and-Bollinger-Bands-Synergy-Trading-System" (RSI + Bollinger Bands Strategy).

FMZ source id: 482775

Source
    https://www.fmz.com/strategy/482775 (PineScript v5, FMZ last modified 2025-02-27 17:51:02).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 102-149), BB 20 x 2.0; RSI 14, 70 / 30; 10 % of equity
    crossover(rsi, 30) and close <= lowerBB -> entry Long;  crossunder(rsi, 70) and close >= upperBB -> entry Short
    crossunder(rsi, 70) or close >= basis -> close Long;  crossover(rsi, 30) or close <= basis -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries come before the closes: an entry that reverses a position stands although the other
      side's close is true on that bar (it acts only on a position held into the bar and not reversed on
      it, as #441963). REVERSAL INTENDED. The 10 % of equity size is sizing. FREQ = "30min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band-touch RSI re-crossings with basis exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_482775_rsi30_70_recross_bb20_touch_basis_exit_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_length": [20, 50],
    "bb_std_dev": [2.0, 1.5],
}
DEFAULT_PARAMS = {"bb_length": 20, "bb_std_dev": 2.0, "rsi_length": 14, "rsi_overbought": 70, "rsi_oversold": 30}


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
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["bb_length"])
    mid, sd = c.rolling(n).mean(), c.rolling(n).std(ddof=0)
    k = float(p["bb_std_dev"])
    up, dn = mid + k * sd, mid - k * sd
    r = _rsi(c, int(p["rsi_length"]))
    ob, os_ = float(p["rsi_overbought"]), float(p["rsi_oversold"])
    r_up = (r > os_) & (r.shift(1) <= os_)
    r_dn = (r < ob) & (r.shift(1) >= ob)
    le = r_up & (c <= dn)
    se = r_dn & (c >= up)
    lx = r_dn | (c >= mid)
    sx = r_up | (c <= mid)
    return le, lx & ~se & ~le, se, sx & ~le & ~se


def portfolio_kwargs(**params):
    return {}
