"""EMA 18 distance turns with extreme MACD crossings, 1-hour bars: from flat, a close far under the EMA 18 turning up with the scaled MACD crossing up below a deep negative level goes long (a short in profit
also reverses); the mirror goes short; a target, a stop and a profit threshold re-expressed as fractions of the price.
Port of FMZ strategy #439963 "基于EMA均线和MACD指标的BTC交易策略EMA-and-MACD-Based-BTC-Trading-Strategy" (EMA50Diff & MACD Strategy).

FMZ source id: 439963

Source
    https://www.fmz.com/strategy/439963 (PineScript v3, FMZ last modified 2024-01-25 12:54:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 112-165), EMA 18; MACD 12 / 26 x 3, signal sma 9; thresholds in price units: diff 8, MACD 80, target validity 65, target 120, stop 650
    macdlong = macd < -80 and signal < -80 and crossover(macd, signal);  long = (short and close < avg - 65 and macdlong) or (flat and diff < -8 and diff > diff[1] and diff[1] < diff[2] and macdlong);  short mirror
    close long when close > avg + 120;  close short when close < avg - 120;  exit(stop = avg -/+ 650)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: every threshold is in price units (BTC scale); each becomes a fraction of the price
      (the reading on BTC near 42000): diff / close against 8 / 42000, macd / close and signal / close
      against 80 / 42000, the profit test against 65 / 42000 of the average price, the target 120 /
      42000 and the stop 650 / 42000 of the fill (sl_stop for both sides). The state loop follows the
      stop so that the entries see the position it leaves. The average price is the fill open. Closes
      come after the entries; a reversal stands (as #438020). strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). The equity / close amount is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed from the fill.
    2 generic: ADAPT, price-unit thresholds -> fractions of the price.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the equity amount stored.
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

NAME = "fmz_439963_ema18_diff_turn_extreme_macd"
FAMILY = "macd_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "scale": [42000.0, 21000.0],
    "ema_len": [18, 50],
}
DEFAULT_PARAMS = {"scale": 42000.0, "ema_len": 18, "diff_thr": 8.0, "macd_thr": 80.0, "valid_thr": 65.0,
                  "target": 120.0, "stop": 650.0}


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
    c = bars_df["close"]
    s = float(p["scale"])
    kd, km, kv = float(p["diff_thr"]) / s, float(p["macd_thr"]) / s, float(p["valid_thr"]) / s
    kt, ks = float(p["target"]) / s, float(p["stop"]) / s
    d = (c - c.ewm(span=int(p["ema_len"]), adjust=False).mean()) / c
    macd = 3 * (c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean())
    sig = macd.rolling(9).mean()
    mf, sf = macd / c, sig / c
    ml = ((mf < -km) & (sf < -km) & (macd > sig) & (macd.shift(1) <= sig.shift(1))).to_numpy()
    ms = ((mf > km) & (sf > km) & (macd < sig) & (macd.shift(1) >= sig.shift(1))).to_numpy()
    d0, d1, d2 = d.to_numpy(), d.shift(1).to_numpy(), d.shift(2).to_numpy()
    with np.errstate(invalid="ignore"):
        turn_up = (d0 < -kd) & (d0 > d1) & (d1 < d2)
        turn_dn = (d0 > kd) & (d0 < d1) & (d1 > d2)
    cv, ov = c.to_numpy(dtype=float), bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, ep, entry_i = 0, np.nan, -1
    for i in range(m):
        if pos == 1 and i >= entry_i and lv[i] <= ep * (1 - ks):
            pos = 0
        elif pos == -1 and i >= entry_i and hv[i] >= ep * (1 + ks):
            pos = 0
        if i + 1 >= m:
            continue
        lng = (pos < 0 and cv[i] < ep * (1 - kv) and ml[i]) or (pos == 0 and turn_up[i] and ml[i])
        sht = (pos > 0 and cv[i] > ep * (1 + kv) and ms[i]) or (pos == 0 and turn_dn[i] and ms[i])
        new = pos
        if lng:
            new = 1
        if sht:
            new = -1
        if new == pos:
            if pos == 1 and cv[i] > ep * (1 + kt):
                lx[i], new = True, 0
            elif pos == -1 and cv[i] < ep * (1 - kt):
                sx[i], new = True, 0
        elif new == 1:
            le[i] = True
        elif new == -1:
            se[i] = True
        if new != pos and new != 0:
            ep, entry_i = ov[i + 1], i + 1
        pos = new
    return le, lx, se, sx, ks


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _run(bars_df, p)
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["stop"]) / float(p["scale"])}


def portfolio_kwargs(**params):
    return {}
