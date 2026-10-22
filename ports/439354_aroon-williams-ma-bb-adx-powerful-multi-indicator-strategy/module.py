"""Point-scored Aroon, Williams %R, Bollinger basis and ADX conditions, long only, 1-hour bars: a buy score of at least 3 (a constant 3 from an input comparison, +1 for a deep Aroon 264 and Williams 130 low, -1
each for ADX(145) >= 14 and Aroon 72 >= -39) goes long; a sell score of at least 3 closes.
Port of FMZ strategy #439354 "Aroon Williams MA BB ADX Powerful Multi indicator Strategy" (Aroon+Williams+MA2+ADX+Aroon Str.).

FMZ source id: 439354

Source
    https://www.fmz.com/strategy/439354 (PineScript v3, FMZ last modified 2024-01-19 14:55:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 247-471), Aroon 264 / 72 / 137 / 62; BB 270 x 2; Williams 130; ADX 14 on DI 145 and DI 150; position inputs -85, 117 / 86, -99, 14, -39 (buy) and 120 (unused), 99, 88 / 96, 9, 35 (sell)
    buy score = (osc1 <= -85 ? 1) + (117 > 86 ? 3) + (wil <= -99 ? 1) + (adx >= 14 ? -1) + (osc2 >= -39 ? -1);  sell score = (close > basis ? 1) + (osc3 >= 99 ? 1) + (88 < 96 ? 3) + (adx2 >= 9 ? -2) + (osc4 <= 35 ? -1)
    entry L when buy score >= 3;  close L when sell score >= 3

Interpretation choices (Pine rules in SURVEY_README.md)
    * Aroon oscillator = 100 (highestbars(high, n + 1) - lowestbars(low, n + 1)) / n; the "ma double"
      tests compare two inputs, so each always adds 3. While an indicator is not yet defined its test is
      false, so both scores start at 3 and the warm-up alternates entries and closes, as written. The
      second ADX calls the first function with DI 150. fixnan holds the last DI value, as written. The
      entry and the close act on the position held at the bar close. Long only. No sizing code. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Aroon, Williams %R, Bollinger basis and ADX levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439354_aroon_williams_adx_score_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pos_wil": [-99, -90],
    "pos_aroon1": [-85, -70],
}
DEFAULT_PARAMS = {"pos_wil": -99, "pos_aroon1": -85, "length_1": 264, "length_2": 72, "length_3": 137,
                  "length_4": 62, "length_bb": 270, "length_wil": 130, "adxlen": 14, "dilen": 145,
                  "dilen_2": 150, "pos_adx": 14, "pos_aroon2": -39, "pos_aroon_3": 99, "pos_adx_2": 9,
                  "pos_aroon_4": 35}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _fixnan(x):
    """Pine's fixnan: an undefined value takes the last defined one (leading values stay undefined)."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), -1)
    idx = np.maximum.accumulate(idx)
    out = np.where(idx >= 0, v[np.clip(idx, 0, None)], np.nan)
    return pd.Series(out, index=x.index)


def _aroon_osc(h, lo, n):
    w = n + 1
    hb = -h.rolling(w).apply(lambda a: np.argmax(a[::-1]), raw=True)     # highestbars: offset of the newest high
    lb = -lo.rolling(w).apply(lambda a: np.argmin(a[::-1]), raw=True)
    return 100 * (hb + n) / n - 100 * (lb + n) / n


def _adx(bars_df, dilen, adxlen):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where(up.isna(), np.where((up > dn) & (up > 0), up, 0.0))
    mdm = dn.where(dn.isna(), np.where((dn > up) & (dn > 0), dn, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, dilen)
    with np.errstate(divide="ignore", invalid="ignore"):
        pl = _fixnan(100 * _rma(pdm, dilen) / trr)
        mi = _fixnan(100 * _rma(mdm, dilen) / trr)
    s = pl + mi
    return 100 * _rma((pl - mi).abs() / s.where(s != 0, 1.0), adxlen)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    o1 = _aroon_osc(h, lo, int(p["length_1"]))
    o2 = _aroon_osc(h, lo, int(p["length_2"]))
    o3 = _aroon_osc(h, lo, int(p["length_3"]))
    o4 = _aroon_osc(h, lo, int(p["length_4"]))
    basis = c.rolling(int(p["length_bb"])).mean()
    nw = int(p["length_wil"])
    hh, ll = h.rolling(nw).max(), lo.rolling(nw).min()
    with np.errstate(divide="ignore", invalid="ignore"):
        wil = 100 * (c - hh) / (hh - ll)
    a1 = _adx(bars_df, int(p["dilen"]), int(p["adxlen"]))
    a2 = _adx(bars_df, int(p["dilen_2"]), int(p["adxlen"]))
    vl = (1 * (o1 <= float(p["pos_aroon1"])) + 3 + 1 * (wil <= float(p["pos_wil"]))
          - 1 * (a1 >= float(p["pos_adx"])) - 1 * (o2 >= float(p["pos_aroon2"])))
    vs = (1 * (c > basis) + 1 * (o3 >= float(p["pos_aroon_3"])) + 3 - 2 * (a2 >= float(p["pos_adx_2"]))
          - 1 * (o4 <= float(p["pos_aroon_4"])))
    buy, sell = (vl >= 3).to_numpy(), (vs >= 3).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1:
            if sell[i]:
                lx[i], pos = True, 0
        elif buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
