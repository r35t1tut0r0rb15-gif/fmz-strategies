"""3kilos, 10-minute bars: long when TEMA 50 of highs is above TEMA 100 of lows and TEMA 350 of closes and
above its own SMA 100, an ATR band trend (3 x EMA 550 of true range) is up and the Heikin Ashi close
rose; short on the mirror. Each entry has a 1 % target and a 3 % stop.
Port of FMZ strategy #427822 "Bitcoin Multi-factor Trading Strategy" ("3kilos").

FMZ source id: 427822

Source
    https://www.fmz.com/strategy/427822 (PineScript v5, FMZ last modified 2023-09-25 18:24:02).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 205-299), TEMA 50 (high) / 100 (low) / 350 (close), ATR 550 x 3, SMA 100
    tema(x, n) = 3 (e1 - e2) + e3 (EMA chain)
    up / dn bands of hl2 -+ 3 atr ratchet with uptrend; uptrend flips on close[1] vs dn[1] / up[1]
    longC = tema1 > tema2 and tema1 > tema3 and uptrend and tema1 > sma(tema1, 100) and haClose > haClose[1]
    shortC mirrors (not uptrend)
    longC -> entry long + exit(limit = close x 1.01, stop = close x 0.97); shortC mirrors

Interpretation choices (Pine rules in SURVEY_README.md; skill section 7)
    * The Heikin Ashi close of the chart's own bars is ohlc4.
    * The bracket is re-issued on every longC bar with that bar's close, so while the signal repeats
      the levels move with the close (a moving stop / target): the house cannot express that, so
      the port keeps the fixed bracket from the fill (sl_stop 0.03, tp_stop 0.01) and marks
      trailing_stop_pending. Pine's levels are from the signal close, the house's from the fill.
    * The date filter is dropped (inTradeWindow is true).
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED.
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket at entry (moving version pending).
    2 generic: PASS, MA lengths, ATR multiple, percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity stored; the bracket quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427822_3kilos_tema_atr_trend"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "short": [50, 25],
    "tp_pct": [1.0, 2.0],
    "sl_pct": [3.0, 1.5],
}
DEFAULT_PARAMS = {"short": 50, "long": 100, "long2": 350, "atr_length": 550, "mult": 3.0,
                  "sma_period": 100, "tp_pct": 1.0, "sl_pct": 3.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _tema(x, n):
    e1 = x.ewm(span=n, adjust=False).mean()
    e2 = e1.ewm(span=n, adjust=False).mean()
    e3 = e2.ewm(span=n, adjust=False).mean()
    return 3 * (e1 - e2) + e3


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    t1, t2, t3 = _tema(h, int(p["short"])), _tema(lo, int(p["long"])), _tema(c, int(p["long2"]))
    sma = t1.rolling(int(p["sma_period"])).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = tr.ewm(span=int(p["atr_length"]), adjust=False, ignore_na=True).mean().where(tr.notna()).to_numpy()
    hl2 = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    up, dn = np.full(m, np.nan), np.full(m, np.nan)
    upt = np.zeros(m, dtype=bool)
    k = float(p["mult"])
    for i in range(m):
        lo_b, hi_b = hl2[i] - k * atr[i], hl2[i] + k * atr[i]
        # up := na(up[1]) ? lo_b : uptrend[1] ? max(lo_b, up[1]) : lo_b   (math.max with na is na)
        if i == 0 or np.isnan(up[i - 1]) or not upt[i - 1]:
            up[i] = lo_b
        else:
            up[i] = max(lo_b, up[i - 1]) if not np.isnan(lo_b) else np.nan
        # dn := na(dn[1]) ? hi_b : uptrend[1] ? hi_b : min(hi_b, dn[1])
        if i == 0 or np.isnan(dn[i - 1]) or upt[i - 1]:
            dn[i] = hi_b
        else:
            dn[i] = min(hi_b, dn[i - 1]) if not np.isnan(hi_b) else np.nan
        if i == 0:
            upt[i] = True
        elif cv[i - 1] > dn[i - 1]:
            upt[i] = True
        elif cv[i - 1] < up[i - 1]:
            upt[i] = False
        else:
            upt[i] = upt[i - 1]
    ha = (o + h + lo + c) / 4
    ha_up = (ha > ha.shift(1)).to_numpy()
    ha_dn = (ha < ha.shift(1)).to_numpy()
    with np.errstate(invalid="ignore"):
        t1v, t2v, t3v, sv = (s.to_numpy() for s in (t1, t2, t3, sma))
        long_c = (t1v > t2v) & (t1v > t3v) & upt & (t1v > sv) & ha_up
        short_c = (t1v < t2v) & (t1v < t3v) & ~upt & (t1v < sv) & ha_dn
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(long_c, index=idx), false, pd.Series(short_c, index=idx), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]) / 100, "tp_stop": float(p["tp_pct"]) / 100}


def portfolio_kwargs(**params):
    return {}
