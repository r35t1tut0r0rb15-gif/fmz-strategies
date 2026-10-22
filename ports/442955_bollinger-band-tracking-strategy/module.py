"""Bollinger touches on a WMA 20 basis, 2-hour bars: the low crossing under the lower band goes long, the high crossing over the upper band goes short (reversal entry on); a tick target (re-expressed as an
ATR multiple) and an immediate tick trailing stop (re-expressed as a percent trail); reversing.
Port of FMZ strategy #442955 "Bollinger Band Tracking Strategy" (BB Strategy (Basic)).

FMZ source id: 442955

Source
    https://www.fmz.com/strategy/442955 (PineScript v4, FMZ last modified 2024-02-27 16:11:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 134-186), WMA 20, deviation 2; trailing stop on: trail_points 0, offset 10000 ticks; limit 20000 ticks; reversal entry on; time filter off; 1 contract, commission 3.02 per contract
    crossunder(low, lower) -> entry Enterlong (long);  crossover(high, upper) -> entry Entershort (revti = na -> short)
    exit("Exit", profit = 20000, trail_points = 0, trail_offset = 10000) for each id

Interpretation choices (Pine rules in SURVEY_README.md)
    * With "Reversal Entry" on, revti is an if without else, so na, and the second entry is a short.
      The trail starts at once (trail_points 0) with a 10000-tick offset: 1000 price units at mintick
      0.1 on the BTC reading, the house percent trail {"type": "percent", "pct": 0.0238, "anchor":
      "high_low"} from the fill (1000 / 42000; stated approximation, as #440833; mark trailing_stop).
      Criterion 2: the 20000-tick target is 2000 price units; as an ATR multiple at the 2-hour ATR(14)
      reading of about 300, a target of 6.67 ATR of the signal bar, shifted one bar inside stops() and
      re-based on the fill. Pine's stdev is the population deviation. strategy.entry reverses: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop.
      The contract size and the per-contract commission are sizing and costs. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; target fixed at entry, the trail a house trail (approximation stated).
    2 generic: ADAPT, tick target -> ATR multiple; tick trail -> percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the contract size and per-contract commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (time filter off).
REVERSAL INTENDED.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442955_wma_band_touch_reversal_trail"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [20, 50],
    "trail_pct": [0.0238, 0.01],
}
DEFAULT_PARAMS = {"length": 20, "trail_pct": 0.0238, "mult": 2.0, "tp_atr": 6.67, "atr_len": 14}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _tp(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return float(p["tp_atr"]) * _rma(tr, int(p["atr_len"])) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    basis = _wma(c, n)
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    up, dn = basis + dev, basis - dev
    lsig = ((lo < dn) & (lo.shift(1) >= dn.shift(1))).to_numpy()
    ssig = ((h > up) & (h.shift(1) <= up.shift(1))).to_numpy()
    tp = _tp(bars_df, p).to_numpy()
    pct = float(p["trail_pct"])
    ov, hv, lv = bars_df["open"].to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, t_, best = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            ref = x if np.isnan(best) else best
            if pos == 1 and (lv[i] <= ref * (1 - pct) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= ref * (1 + pct) or lv[i] <= x * (1 - t_)):
                pos = 0
            if pos == 1:
                best = hv[i] if np.isnan(best) else max(best, hv[i])
            elif pos == -1:
                best = lv[i] if np.isnan(best) else min(best, lv[i])
        if i + 1 < m and not np.isnan(tp[i]):
            if ssig[i] and pos != -1:
                se[i], pos, entry_i, t_, best = True, -1, i + 1, tp[i], np.nan
            elif lsig[i] and pos != 1:
                le[i], pos, entry_i, t_, best = True, 1, i + 1, tp[i], np.nan
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": _tp(bars_df, p).shift(1),
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
