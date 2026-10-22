"""Close crossings back inside the Bollinger 20 / 2 bands on the side of the SMA 200, 3-hour bars: crossing over the lower band with the close and basis above the SMA goes long, crossing under the upper band below it goes short; a close at the far band closes; the 3 % stop is taken from the price of the position held at the signal (none from flat); reversing.
Port of FMZ strategy #476259 "Dynamic Moving Average and Bollinger Bands Cross Strategy with Fixed Stop Loss Optimization Model" (MA 200 and Bollinger Bands Strategy).

FMZ source id: 476259

Source
    https://www.fmz.com/strategy/476259 (PineScript v5, FMZ last modified 2024-12-27 14:57:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 145-203), SMA 200; BB 20 / 2; stop 3 % of strategy.position_avg_price
    close > sma200 and basis > sma200 and crossover(close, lower) -> entry Long, exit(Long, stop = avg x 0.97);  close < sma200 and basis < sma200 and crossunder(close, upper) -> entry Short, exit(Short, stop = avg x 1.03)
    close >= upper -> close Long;  close <= lower -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is sent on the signal bar from strategy.position_avg_price, which is still the price of
      the position held then: na from flat (no stop), and the replaced position's fill price on a
      reversal, as written (as #473147); a loop tracks those prices and the level is sent as a fraction of
      the new fill open (a level at or through it is marketable and closed one bar late). A repeat signal
      while held arms a stop 3 % from that position's own price; that re-send is not followed (as #437800,
      mark trailing_stop_pending). The band closes are bar-close tests filled at the next open; a close
      acts only on the held position and leaves a same-bar reversal standing. REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No
      sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the replaced position's price as the stop base, as written.
    2 generic: PASS, Bollinger re-entries on the SMA 200 side with band closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_476259_bb20_reentry_sma200_side_band_close_avg_stop_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bb_length": [20, 50],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"bb_length": 20, "ma_length": 200, "bb_mult": 2.0, "sl_pct": 0.03}


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


def _run(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ma = c.rolling(int(p["ma_length"])).mean()
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    lc = ((c > ma) & (basis > ma) & (c > dn) & (c.shift(1) <= dn.shift(1))).to_numpy()
    sc = ((c < ma) & (basis < ma) & (c < up) & (c.shift(1) >= up.shift(1))).to_numpy()
    cl_l = (c >= up).to_numpy()
    cl_s = (c <= dn).to_numpy()
    ov, hv, lv = (x.to_numpy(dtype=float) for x in (o, h, lo))
    slp = float(p["sl_pct"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    sl_sent, side = np.full(m, np.nan), np.zeros(m)
    pos, pend, avg, sl, sl_n = 0, 0, np.nan, np.nan, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, pend, avg, sl = pend, 0, ov[i], sl_n
            through = (sl >= ov[i]) if pos == 1 else (sl <= ov[i])
            if through:                          # a level through the fill: closed at the next open
                if pos == 1:
                    lx[i] = True
                else:
                    sx[i] = True
                pend, sl = 2, np.nan
        elif pend == 2:
            pos, pend, avg, sl = 0, 0, np.nan, np.nan
        if pos == 1 and lv[i] <= sl:
            pos, avg, sl = 0, np.nan, np.nan     # the stop fills inside this bar
        elif pos == -1 and hv[i] >= sl:
            pos, avg, sl = 0, np.nan, np.nan
        if pend == 2:
            continue
        if lc[i] and pos != 1:
            sl_n = avg * (1 - slp)               # na from flat
            le[i], pend, sl_sent[i], side[i] = True, 1, sl_n, 1
        elif sc[i] and pos != -1:
            sl_n = avg * (1 + slp)
            se[i], pend, sl_sent[i], side[i] = True, -1, sl_n, -1
        if pos == 1 and cl_l[i] and not se[i]:
            lx[i], pend = True, 2
        elif pos == -1 and cl_s[i] and not le[i]:
            sx[i], pend = True, 2
    ix = bars_df.index
    return [pd.Series(x, index=ix) for x in (le, lx, se, sx, sl_sent, side)]


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return tuple(_run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl_l, sd = _run(bars_df, p)[4:]
    o = bars_df["open"]
    sl_l, sd = sl_l.shift(1), sd.shift(1)    # the signal bar's level, read at the fill
    sl_f = (1 - sl_l / o).where(sd > 0, sl_l / o - 1)
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
