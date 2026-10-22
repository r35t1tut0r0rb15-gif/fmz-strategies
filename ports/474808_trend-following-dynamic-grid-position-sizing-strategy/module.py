"""TTM-state grid, 1-minute bars: a close in the top third of the EMA 6 high / low channel sets a buy grid at that close, in the bottom third a sell grid; with a buy grid a low 1-5 % under the base goes long and a high 1-5 % over it goes short, with a sell grid the mirror; the last order sent on a bar sets the position; reversing.
Port of FMZ strategy #474808 "Trend Following Dynamic Grid Position Sizing Strategy" (TTM Grid Strategy).

FMZ source id: 474808

Source
    https://www.fmz.com/strategy/474808 (PineScript v5, FMZ last modified 2024-12-12 11:19:17).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 124-212), TTM period 6; 5 grid levels; spacing 0.01 (a fraction: 1 % steps)
    state = close > highThird ? 1 : close < lowThird ? 0 : -1;  state != -1 and state != dir -> base := close, dir := state;  for i in 1..5: dir == 1: low <= base (1 - 0.01 i) -> entry GridBuy_i, high >= base (1 + 0.01 i) -> entry GridSell_i;  else: high >= base (1 + 0.01 i) -> entry GridBuy_i, low <= base (1 - 0.01 i) -> entry GridSell_i

Interpretation choices (Pine rules in SURVEY_README.md)
    * The spacing input is used as a fraction (i x 0.01), so the levels are 1 % apart, as written. The
      base and direction are kept in a loop from the script's seeds (base 0, direction -1, which makes
      every high reach the sell grid's buy level until the first state). With pyramiding 1 the grid ids
      never add up: all entry calls of a bar are sent in order (buy, sell for each level) and the last
      one sets the position (#437773); a same-side entry while held is ignored. There is no exit:
      positions end at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, TTM-state grid levels, one position at a time.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_474808_ttm_state_grid_1pct_levels_last_order_reversal"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ttm_period": [6, 12],
    "spacing": [0.01, 0.02],
}
DEFAULT_PARAMS = {"ttm_period": 6, "spacing": 0.01, "levels": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["ttm_period"])
    lm, hm = lo.ewm(span=n, adjust=False).mean(), h.ewm(span=n, adjust=False).mean()
    lt = ((hm - lm) / 3 + lm).to_numpy(dtype=float)
    ht = (2 * (hm - lm) / 3 + lm).to_numpy(dtype=float)
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    sp, k = float(p["spacing"]), int(p["levels"])
    st = np.where(cv > ht, 1, np.where(cv < lt, 0, -1))
    m = len(cv)
    bases, dirs = np.zeros(m), np.full(m, -1)
    base, d = 0.0, -1
    for i in range(m):
        if st[i] != -1 and st[i] != d:
            base, d = cv[i], st[i]
        bases[i], dirs[i] = base, d
    last = np.zeros(m, dtype=int)                # the last entry call of the bar, in the written order
    buy_grid = dirs == 1
    for j in range(1, k + 1):
        dn_hit = lv <= bases * (1 - j * sp)
        up_hit = hv >= bases * (1 + j * sp)
        first_call = np.where(buy_grid, dn_hit, up_hit)          # GridBuy_j
        second_call = np.where(buy_grid, up_hit, dn_hit)         # GridSell_j
        last = np.where(first_call, 1, last)
        last = np.where(second_call, -1, last)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if last[i] == 1 and pos != 1:
            le[i], pos = True, 1
        elif last[i] == -1 and pos != -1:
            se[i], pos = True, -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
