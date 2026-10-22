"""Opens jumping across an SMA 37 +- 0.2 ATR(37) range, 3-hour bars: an open above the range after an open below it, also above the EMA 74 + the band, goes long, the mirror short; a fixed target and stop
from the entry (tick distances, re-expressed as ATR multiples); reversing.
Port of FMZ strategy #442644 "基于ATR和EMA的趋势跟随策略All-about-the-ATR-and-EMA-based-trend-following-strategy" (cATRpillar).

FMZ source id: 442644

Source
    https://www.fmz.com/strategy/442644 (PineScript v4, FMZ last modified 2024-02-23 14:34:24).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 128-184), lookback 37; range 0.2 ATR; take profit 5000, stop 2500 (ticks); lots 1
    atrLong = open[1] < rangeLo and open > rangeHi;  longCondition = atrLong and open > ema(74) + atr -> entry Buy;  shortCondition = atrShort and open < ema - atr -> entry Sell
    exit(cATRpillar-Exit, qty = 1, profit = 5000, loss = 2500, when = open > rangeLo);  same id, when = open < rangeHi

Interpretation choices (Pine rules in SURVEY_README.md)
    * The signals read the bar's own open, known at its close. One of the two exit conditions holds on
      every bar (an open above rangeHi is above rangeLo), so the shared exit is always in place, at the
      full 1-lot default size. Criterion 2: the 5000 / 2500-tick target and stop are 500 / 250 price
      units at mintick 0.1 on the BTC reading; as ATR multiples at a 3-hour ATR(14) reading of about 350
      (between the 2-hour 300 and 4-hour 400 readings), a target of 1.43 ATR and a stop of 0.714 ATR of
      the signal bar, shifted one bar inside stops() and re-based on the fill. strategy.entry reverses:
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour bars: mark
      coarse_bar_stop. The lot size is sizing. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot quantity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442644_open_jump_atr_range_ema_filter_bracket"
FAMILY = "volatility_channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [37, 20],
    "atr_mult": [0.2, 0.5],
}
DEFAULT_PARAMS = {"lookback": 37, "atr_mult": 0.2, "tp_atr": 1.43, "sl_atr": 0.714, "atr_len": 14}


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


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)


def _fractions(bars_df, p):
    a = _rma(_tr(bars_df), int(p["atr_len"])) / bars_df["close"]
    return float(p["sl_atr"]) * a, float(p["tp_atr"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["lookback"])
    band = _rma(_tr(bars_df), n) * float(p["atr_mult"])
    sma = c.rolling(n).mean()
    ema = c.ewm(span=n * 2, adjust=False).mean()
    rlo, rhi = sma - band, sma + band
    o1 = o.shift(1)
    lsig = ((o1 < rlo) & (o > rhi) & (o > ema + band)).to_numpy()
    ssig = ((o1 > rhi) & (o < rlo) & (o < ema - band)).to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
