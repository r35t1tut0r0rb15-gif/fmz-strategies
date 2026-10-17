"""EMA 9 / 21 cross-up buys from flat with a cooldown and two close-checked trails, safety orders not ported, long only,
hourly bars: EMA 9 crossing above EMA 21 goes long when flat (not within 4 bars of the last base entry); a close 8 %
below the highest close since entry, a close 1.5 % below the peak once the trade has gained 2.5 %, or EMA 9 crossing
below EMA 21 closes it.
Port of FMZ strategy #490570 "智能波动跟踪型DCA策略与双轨止损系统-Intelligent-Volatility-Responsive-DCA-Strategy-with-Dual-Trailing-Stop-System" (BONK/USD (1H) - $4k DCA + Dual Trailing + Date Filter).

FMZ source id: 490570

Source
    https://www.fmz.com/strategy/490570 (PineScript v5, FMZ last modified 2025-04-14 18:18:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 199-343), EMA 9 / 21, trail 8 %, lock-in at +2.5 % with a 1.5 % trail, cooldown 4
    base = crossover(ema9, ema21) and flat and bar_index - lastBuyBar >= 4 -> base order (long)
    safety orders 1 / 2 at base - 1.2 / 2.5 ATR (adds)
    in position: highest close since entry; stop when close < highest x 0.92; once close >= avg entry x 1.025, a peak
    close trail: stop when close < peak x 0.985; crossunder(ema9, ema21) -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The safety orders are averaging in (sizing, criterion 4): quoted in original_sizing.txt, not ported. Without
      them the average entry is the base fill (the open of the bar after the signal).
    * Both trails are checked on closes: close-based exit signals (rule 2 / 3), no mark. The highest close and the
      lock-in start from the first bar held (the fill bar), as written.
    * The cooldown counts bars from the base signal bar. Long only; Opposite entries cannot occur.
    * The commission in strategy() is a cost (not in the module). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and close-checked trails.
    2 generic: PASS, EMAs and percentages (the ATR-spaced adds are sizing).
    3 crypto-exchange-only: no (3Commas alert texts only).
    4 signals only: base / safety order sizes and the adds quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG490570 (2 members, best partner #490797, Jaccard 0.910); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_490570_ema_cross_dual_close_trail_long"
FAMILY = "ma_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [8.0, 4.0],
    "lock_in_trail_pct": [1.5, 3.0],
}
DEFAULT_PARAMS = {"fast": 9, "slow": 21, "trail_pct": 8.0, "lock_in_threshold_pct": 2.5, "lock_in_trail_pct": 1.5,
                  "cooldown_bars": 4}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    up = ((ef > es) & (ef.shift(1) <= es.shift(1))).to_numpy()
    dn = ((ef < es) & (ef.shift(1) >= es.shift(1))).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tr, lk_th, lk_tr = p["trail_pct"] / 100, p["lock_in_threshold_pct"] / 100, p["lock_in_trail_pct"] / 100
    cool = int(p["cooldown_bars"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False            # strategy.position_size > 0 at this bar (filled at its open)
    pending = False         # entry signalled on the previous bar
    last_buy = None
    hi = peak = avg = np.nan
    locked = False
    for i in range(m):
        if pending:
            held, pending, avg = True, False, ov[i]
        if up[i] and not held and not pending and (last_buy is None or i - last_buy >= cool):
            le[i], pending, last_buy = True, True, i
        stop_n = stop_l = False
        if held:
            hi = cv[i] if np.isnan(hi) else max(hi, cv[i])
            stop_n = cv[i] < hi * (1 - tr)
            if not locked and cv[i] >= avg * (1 + lk_th):
                locked, peak = True, cv[i]
            if locked:
                peak = max(peak, cv[i])
                stop_l = cv[i] < peak * (1 - lk_tr)
        else:
            hi = peak = np.nan
            locked = False
        if held and (stop_n or stop_l or dn[i]):
            lx[i] = True
            held, hi, peak, locked = False, np.nan, np.nan, False
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false, false.copy()


def portfolio_kwargs(**params):
    return {}
