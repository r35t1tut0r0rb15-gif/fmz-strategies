"""Hourly bars: the upper Keltner line (EMA 20 +- 2.2 x EMA 20 of the true range) crossing over the upper Bollinger band (20, 2) on above-average volume (SMA 10) goes long; the lower Keltner line crossing under the lower band on above-average volume goes short; each position closes after about 20 bars; reversing.
Port of FMZ strategy #440086 "渐进BB-KC趋势策略Gradual-BB-KC-Trend-Strategy" (BB and KC Strategy (jensenvilhelm)).

FMZ source id: 440086

Source
    https://www.fmz.com/strategy/440086 (PineScript v5, FMZ last modified 2024-01-26 15:10:41).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 116-176), KC 20 x 2.2; BB 20 x 2; volume SMA 10; stop 1.5 %, trail 2 % (sent with the close); 20 bars in trade
    longCond = crossover(kc_upper, bb_upper) and volume > sma(volume, 10) -> entry Buy, bar_counter := 1;  shortCond mirror -> entry Sell, bar_counter := 1
    if position_size != 0: bar_counter += 1;  bar_counter > 20 -> close_all (and exit stops sent the same bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * bar_counter restarts at 1 on every signal bar (also a repeated one while already in that
      position) and counts the bars with a position, so a position from flat closes at the open after
      its 20th bar; one opened by a reversal one bar sooner. The stop / trail exits are sent only on the
      bar the close_all is sent, so the market close takes the position first and they never act
      (trail_points without trail_offset does not trail). ta.kc uses the true range. REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bar-count exit.
    2 generic: PASS, Keltner / Bollinger band crossings on above-average volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against its SMA 10; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440086_keltner_bollinger_band_cross_volume_20bar_exit_1h_reversal"
FAMILY = "keltner_channel"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kc_mult": [2.2, 1.5],
    "bars_in_trade": [20, 40],
}
DEFAULT_PARAMS = {"kc_len": 20, "kc_mult": 2.2, "bb_len": 20, "bb_mult": 2.0, "vol_len": 10, "bars_in_trade": 20}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    bl = int(p["bb_len"])
    basis = c.rolling(bl).mean()
    sd = c.rolling(bl).std(ddof=0)
    bb_up, bb_dn = basis + float(p["bb_mult"]) * sd, basis - float(p["bb_mult"]) * sd
    kl = int(p["kc_len"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    mid = c.ewm(span=kl, adjust=False).mean()
    rng = tr.ewm(span=kl, adjust=False).mean()
    kc_up, kc_dn = mid + rng * float(p["kc_mult"]), mid - rng * float(p["kc_mult"])
    vol_ok = v > v.rolling(int(p["vol_len"])).mean()
    lc = ((kc_up > bb_up) & (kc_up.shift(1) <= bb_up.shift(1)) & vol_ok).to_numpy()
    sc = ((kc_dn < bb_dn) & (kc_dn.shift(1) >= bb_dn.shift(1)) & vol_ok).to_numpy()
    k = int(p["bars_in_trade"])
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    tgt, counter = 0, np.nan
    for i in range(m):
        held = tgt                                     # the position during bar i
        new = tgt
        if lc[i]:
            counter = 1
            if new != 1:
                new = 1
        if sc[i]:
            counter = 1
            if new != -1:
                new = -1
        if held != 0 and not np.isnan(counter):
            counter += 1
        if not np.isnan(counter) and counter > k:
            new = 0
        if new != tgt:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif tgt == 1:
                lx[i] = True
            else:
                sx[i] = True
            tgt = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
