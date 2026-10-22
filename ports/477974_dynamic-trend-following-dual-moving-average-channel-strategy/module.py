"""A channel of the SMA 10 of highs and SMA 8 of lows, 10-minute bars, long only: the fifth consecutive bar with its low above the upper line buys from flat; the fifth consecutive bar with its high below the lower line closes, and so does a low 25 % under the highest high since the signal bar.
Port of FMZ strategy #477974 "Dynamic Trend Following Dual Moving Average Channel Strategy with Risk Management System" (Moving Average Channel (MAC)).

FMZ source id: 477974

Source
    https://www.fmz.com/strategy/477974 (PineScript v5, FMZ last modified 2025-01-10 16:26:56).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-150), upper SMA 10 of high, lower SMA 8 of low; 5-bar counts; stop 25 % under the highest high; 100 % of equity
    low > upper -> upCount += 1 else 0;  high < lower -> dnCount += 1 else 0;  upCount == 5 and flat -> entry Long, highest := high
    long -> highest := max(highest, high);  dnCount == 5 and long -> close;  low < highest x 0.75 and long -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes are bar-close tests filled at the next open, so a loop follows the counters and the
      highest high as written (it starts at the signal bar's high). A comparison with a line still in
      its warm-up is false, so the counters also count those bars, as Pine's else branch does. Long only. The 100 % of equity size is
      sizing. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, channel persistence entries with a channel exit and a deep high-water stop.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity stored, not ported.
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

NAME = "fmz_477974_ma_channel_5bar_persistence_long"
FAMILY = "channel_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "count": [5, 3],
    "stop_pct": [0.25, 0.05],
}
DEFAULT_PARAMS = {"count": 5, "stop_pct": 0.25, "upper_len": 10, "lower_len": 8}


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
    h, lo = bars_df["high"], bars_df["low"]
    up = h.rolling(int(p["upper_len"])).mean().to_numpy()
    dn = lo.rolling(int(p["lower_len"])).mean().to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    need = int(p["count"])
    keep = 1 - float(p["stop_pct"])
    m = len(hv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt, uc, dc, hi = 0, 0, 0, 0, np.nan
    for i in range(m):
        pos = nxt
        uc = 0 if lv[i] <= up[i] else uc + 1         # a na line counts, as Pine's else branch
        dc = 0 if hv[i] >= dn[i] else dc + 1
        if uc == need and pos == 0:
            le[i], nxt, hi = True, 1, hv[i]
        if pos == 1:
            hi = hv[i] if np.isnan(hi) else max(hi, hv[i])
        if pos == 1 and (dc == need or lv[i] < hi * keep):
            lx[i], nxt = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
