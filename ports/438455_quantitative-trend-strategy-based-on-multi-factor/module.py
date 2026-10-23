"""Hourly volume-spread analysis, long only: an up bar after a wide-range "reverse upthrust" bar in a major and minor downtrend (up close on rising, above-average volume after a down bar with a down close), or an up bar with an up close after a low-volume test of the 5-bar low, goes long; a wide-range "true upthrust" bar (close in the bottom fifth, above-average volume, a new high over the previous bar, in a major uptrend) closes it.
Port of FMZ strategy #438455 "Quantitative Trend Strategy Based on Multi factor" (volume spread analysis).

FMZ source id: 438455

Source
    https://www.fmz.com/strategy/438455 (PineScript v3, FMZ last modified 2024-01-12 11:09:40).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 136-296), volume SMA 40; spread SMA 80; random-walk index 2 / 8 (short) and 10 / 40 (long); long only
    buy = (upbar and revupthrust[1]) or lowvoltest2 -> entry simpleBuy;  close(simpleBuy) when upthrustbartrue
    revupthrust = upmajor < 0 and upbar and upclose and volume > volume[1] and volume > volavg and widerangebar and downbar[1] and downclose[1] and upminor < 0

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only buy, revupthrust, lowvoltest2 and upthrustbartrue feed orders; the other VSA labels feed
      plots only. upmajor is the sign of j = rwhs - rwls (random-walk index of highs minus lows, short
      term 2 / 8) beyond +-1, 0 inside or before it exists; upminor is +1 when the long-term random-walk
      index of highs (10 / 40) exceeds 1, else -1 (also before it exists). nz(low[n]) only matters
      before the ATR exists, so it changes nothing. ATR as Pine's rma of the true range. volpos < 4 is
      volume above its 40-bar average. strategy.entry while long adds nothing (pyramiding 0); the close
      never acts on the entry's own bar. Long only. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, volume-spread-analysis bar patterns.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volavg (SMA 40), the rising-volume and low-volume tests and volpos; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438455_vsa_reverse_upthrust_low_volume_test_1h_long_only"
FAMILY = "volume_state"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_len": [40, 20],
    "spread_len": [80, 40],
}
DEFAULT_PARAMS = {"vol_len": 40, "spread_len": 80, "st_min": 2, "st_max": 8, "lt_min": 10, "lt_max": 40}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())

    def rwi(n):
        den = _rma(tr, n) * np.sqrt(n)
        return (h - lo.shift(n)) / den, (h.shift(n) - lo) / den

    hs1, ls1 = rwi(int(p["st_min"]))
    hs2, ls2 = rwi(int(p["st_max"]))
    hl1, _ = rwi(int(p["lt_min"]))
    hl2, _ = rwi(int(p["lt_max"]))
    rwhs = pd.concat([hs1, hs2], axis=1).max(axis=1, skipna=False)
    rwls = pd.concat([ls1, ls2], axis=1).max(axis=1, skipna=False)
    j = rwhs - rwls
    j2 = pd.concat([hl1, hl2], axis=1).max(axis=1, skipna=False)
    maj_up, maj_dn = (j > 1), (j < -1)
    min_dn = ~(j2 > 1)
    volavg = v.rolling(int(p["vol_len"])).mean()
    spread = h - lo
    avgspread = spread.rolling(int(p["spread_len"])).mean()
    wide = spread > 1.5 * avgspread
    upbar, downbar = c > pc, c < pc
    upclose = c >= spread * 0.7 + lo
    downclose = c <= spread * 0.3 + lo
    closepos1 = c <= spread * 0.2 + lo
    lowvol = (v < v.shift(1)) & (v < v.shift(2))
    revup = (maj_dn & upbar & upclose & (v > v.shift(1)) & (v > volavg) & wide
             & downbar.shift(1, fill_value=False) & downclose.shift(1, fill_value=False) & min_dn)
    lowvoltest = (lo == lo.rolling(5).min()) & upclose & lowvol
    lowvoltest2 = lowvoltest.shift(1, fill_value=False) & upbar & upclose
    buy = ((upbar & revup.shift(1, fill_value=False)) | lowvoltest2).to_numpy()
    sell = (wide & closepos1 & maj_up & (h > h.shift(1)) & (v > volavg)).to_numpy()
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 1 and sell[i]:
            lx[i], pos = True, 0
        elif pos == 0 and buy[i]:
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
