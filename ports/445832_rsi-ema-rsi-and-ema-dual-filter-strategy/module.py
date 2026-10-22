"""RSI 2 extremes with the EMA 50 / 200 trend, 1-hour bars: RSI 2 under 10 with the EMA 50 above the EMA 200 and the close above it goes long, RSI 2 over 90 in the mirror trend goes short; reversing; the
moving stop and trailing stop are not ported, and the short's stop sits under the price, so each short closes at the next open after its fill.
Port of FMZ strategy #445832 "RSI与EMA双重过滤策略RSI-and-EMA-Dual-Filter-Strategy" (RSI2).

FMZ source id: 445832

Source
    https://www.fmz.com/strategy/445832 (PineScript v4, FMZ last modified 2024-03-22 15:37:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-255), RSI 2 (rma form), levels 90 / 10; EMA 200 / 50; trend filter on; tick 0.5; trailing 1 %; stop 0.3 % of the current close; 5-minute re-entry guard
    fast > slow and close > slow and rsi < 10 -> entry RSILong;  fast < slow and close < slow and rsi > 90 -> entry RSIShort  (each at most once per 5 minutes)
    exit(RSILong / RSIShort, when = 5 minutes since that entry, trail_points = 0, trail_offset = close / 0.5 x 1 %, stop = close x (1 - 0.3 %))  (re-sent every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * On 1-hour bars the 5-minute guards only block a second entry on the entry bar itself, and the
      exits are sent from the bar after the signal (the fill bar) on. Both exits use stop = close x
      0.997 of the bar sending them: for a long a stop that moves with the price after entry (up or
      down), together with a trailing stop whose offset is 1 % of the close in the author's tick units:
      stops() cannot express the moving stop, so neither is ported (mark trailing_stop_pending; the
      intended stops are owed). For a short that stop is a buy stop under the price, on the wrong side
      of the market, so the short closes at the first open after its fill bar (as #439872). Longs end
      at the short entries meanwhile. The rsi formula is the script's own (down == 0 -> 100, up == 0 ->
      0). REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the long's moving stops not ported (mark); the short's wrong-side stop read as a close.
    2 generic: PASS, RSI 2 extremes with an EMA trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the tick, trailing and stop inputs quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_445832_rsi2_extremes_ema50_200_trend_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "slow_len": [200, 100],
    "rsi_dn": [10, 5],
}
DEFAULT_PARAMS = {"slow_len": 200, "fast_len": 50, "rsi_dn": 10.0, "rsi_up": 90.0, "rsi_len": 2}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = c.diff()
    n = int(p["rsi_len"])
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        base = 100 - 100 / (1 + up / dn)
    rsi = np.where(dn == 0, 100.0, np.where(up == 0, 0.0, base))   # na stays na
    slow = c.ewm(span=int(p["slow_len"]), adjust=False).mean()
    fast = c.ewm(span=int(p["fast_len"]), adjust=False).mean()
    cv = c.to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        lc = ((fast > slow) & (c > slow)).to_numpy() & (rsi < float(p["rsi_dn"]))
        sc = ((fast < slow) & (c < slow)).to_numpy() & (rsi > float(p["rsi_up"]))
    m = len(cv)
    le, se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, sfill = 0, -1
    for i in range(m):
        new = pos
        if pos == -1 and i >= sfill and not sc[i]:
            sx[i], new = True, 0                    # wrong-side buy stop: out at the next open
            # (a repeated short signal resets the 5-minute guard, so no exit is sent on that bar)
        if lc[i] and pos != 1:
            le[i], sx[i], new = True, False, 1
        if sc[i] and pos != -1:
            se[i], new = True, -1
            sfill = i + 1
        pos = new
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
