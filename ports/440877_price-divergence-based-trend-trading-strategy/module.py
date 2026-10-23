"""Two-hour bars: a bullish divergence (regular or hidden) between a 5-bar fractal low of price and of the SMA-based MACD histogram (12 / 26 / 9), with the Murrey math oscillator (100 bars) above 0.25 on the previous bar, goes long; the bearish mirror with the oscillator under -0.25 goes short; the oscillator crossing back through 0 closes each; reversing.
Port of FMZ strategy #440877 "Price Divergence Based Trend Trading Strategy" ([STRATEGY][UL]Price Divergence Strategy v1.0 (JustUncleL)).

FMZ source id: 440877

Source
    https://www.fmz.com/strategy/440877 (PineScript v2, FMZ last modified 2024-02-02 18:00:55).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 177-318), method 1 (MACD histogram, SMA 12 / 26, EMA 9 signal); hidden and regular divergence; MMLO length 100, quadrant 2; trail 100 points with no offset; TP / SL off
    fractal_top = f_fractalize(hist) > 0 ? hist[2] : na;  regular_bearish_div = fractal_top and high[2] > high_price and hist[2] < high_prev (valuewhen(fractal_top, ..., 1));  hidden mirror
    enterLong = (regular_bullish_div or hidden_bullish_div) and b[1] (oscillator[1] > 0.25);  exitLong = oscillator <= 0;  enterShort with y[1] (oscillator[1] < -0.25);  exitShort = oscillator >= 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * f_macd returns its last line, the histogram. A fractal is a 5-bar pattern whose middle bar (two
      bars ago) is the extreme; the previous fractal's value and price come from valuewhen(..., 1). The
      exit has trail_points 100 but no trail offset and no profit / loss, so it never acts. A close acts
      only on a position the bar's entries leave unchanged. Volume feeds only the unused methods: volume
      is not used. REVERSAL INTENDED. 10 % of equity is sizing. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MACD-histogram fractal divergences confirmed by the Murrey math oscillator.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 10 % of equity, capital 10000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440877_macd_hist_fractal_divergence_murrey_osc_2h_reversal"
FAMILY = "macd_variant"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [100, 50],
    "quad": [2, 1],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "smooth": 9, "length": 100, "quad": 2}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _divergences(x, price, side):
    """Fractal divergences of x against price (side +1: tops vs highs, -1: bottoms vs lows):
    returns (regular, hidden) as written, using the previous fractal (valuewhen(..., 1))."""
    s = x if side > 0 else -x
    frac = ((s.shift(4) < s.shift(2)) & (s.shift(3) < s.shift(2)) & (s.shift(2) > s.shift(1)) & (s.shift(2) > s)).to_numpy()
    xv, pv = x.shift(2).to_numpy(dtype=float), price.shift(2).to_numpy(dtype=float)
    m = len(frac)
    reg, hid = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    last_x = last_p = np.nan
    for i in range(m):
        truthy = frac[i] and xv[i] != 0 and not np.isnan(xv[i])   # the fractal value is the condition
        if truthy:
            if not np.isnan(last_x):
                if side > 0:
                    reg[i] = pv[i] > last_p and xv[i] < last_x
                    hid[i] = pv[i] < last_p and xv[i] > last_x
                else:
                    reg[i] = pv[i] < last_p and xv[i] > last_x
                    hid[i] = pv[i] > last_p and xv[i] < last_x
            last_x, last_p = xv[i], pv[i]
    return reg, hid


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    macd = c.rolling(int(p["fast"])).mean() - c.rolling(int(p["slow"])).mean()
    hist = macd - macd.ewm(span=int(p["smooth"]), adjust=False).mean()
    rb_r, rb_h = _divergences(hist, h, 1)
    bu_r, bu_h = _divergences(hist, lo, -1)
    n = int(p["length"])
    hi, lw = h.rolling(n).max(), lo.rolling(n).min()
    rng = hi - lw
    osc = (c - (lw + rng * 0.125 * 4)) / (rng / 2).where(rng != 0)
    q = int(p["quad"])
    lvl = 0.125 * 2 * (q - 1)
    up_q = ((osc > 0) & (osc > lvl)).shift(1, fill_value=False).to_numpy()
    dn_q = ((osc < 0) & (osc < -lvl)).shift(1, fill_value=False).to_numpy()
    go_l = (bu_r | bu_h) & up_q
    go_s = (rb_r | rb_h) & dn_q
    ex_l, ex_s = (osc <= 0).to_numpy(), (osc >= 0).to_numpy()
    m = len(go_l)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if go_l[i] and new != 1:
            new = 1
        if go_s[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and ex_l[i]:
                new = 0
            elif pos == -1 and ex_s[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
