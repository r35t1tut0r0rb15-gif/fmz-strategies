"""The volume flow indicator (8-bar sum of capped, direction-signed volume over the average volume, EMA 3) with an EMA 50 / 200 trend filter, 3-minute bars, long only: the VFI crossing over -4 with the EMA 50 at or above the EMA 200 goes long; the VFI crossing under 5 closes it when the close is above the entry, or more than 5 % below it.
Port of FMZ strategy #428887 "Trend Following Strategy Based on Volume Flow Indicator" (VFI strategy [based on VFI indicator published by UTS]).

FMZ source id: 428887

Source
    https://www.fmz.com/strategy/428887 (PineScript v4, FMZ last modified 2023-10-10 14:51:13).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 180-293), VFI length 8, coef 0.2, volume cutoff 2.5, EMA 3 smoothing; buy line -4, sell line 5; stop 5 %; EMA 200 / 50; pyramiding 2
    vCp = mf > 0.2 x stdev(log returns of hlc3, 30) x close ? min(volume, 2.5 x sma(volume[1], 8)) : mf < -cutoff ? -min(...) : 0;  vfi = ema(sum(vCp, 8) / sma(volume[1], 8), 3)
    crossover(vfi, -4) and ema(50) >= ema(200) -> entry VFI LE;  crossunder(vfi, 5) and close > avg -> close;  crossunder(vfi, 5) and close < avg x 0.95 -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits need the VFI to cross under 5; between 0.95 x and 1 x the entry the crossing leaves the
      trade open, as written. The adds that pyramiding 2 allows are sizing: the port holds one position.
      The exits are close tests against the fill. Long only. The fixed quantity is sizing. FREQ = "3min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-based exits.
    2 generic: PASS, volume flow indicator crossings with an EMA trend filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed quantity, pyramiding 2, capital 10000 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VFI (capped signed volume over its average); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428887_volume_flow_indicator_cross_ema50_200_filter_long"
FAMILY = "volume_flow"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vfi_length": [8, 130],
    "buy_line": [-4.0, 0.0],
}
DEFAULT_PARAMS = {"vfi_length": 8, "buy_line": -4.0, "sell_line": 5.0, "coef": 0.2, "vcoef": 2.5, "smooth": 3,
                  "stop": 5.0}


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
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    n = int(p["vfi_length"])
    avg = (h + lo + c) / 3
    inter = np.log(avg) - np.log(avg.shift(1))
    cut = float(p["coef"]) * inter.rolling(30).std(ddof=0) * c
    vave = v.shift(1).rolling(n).mean()
    vc = np.minimum(v, vave * float(p["vcoef"]))
    mf = avg - avg.shift(1)
    vcp = pd.Series(np.where(mf > cut, vc, np.where(mf < -cut, -vc, 0.0)), index=c.index)
    vfi = (vcp.rolling(n).sum() / vave).ewm(span=int(p["smooth"]), adjust=False).mean()
    trend = c.ewm(span=50, adjust=False).mean() >= c.ewm(span=200, adjust=False).mean()
    bl, sl_ = float(p["buy_line"]), float(p["sell_line"])
    ent = ((vfi > bl) & (vfi.shift(1) <= bl) & trend).to_numpy()
    xd = ((vfi < sl_) & (vfi.shift(1) >= sl_)).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    k = float(p["stop"]) / 100
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill = 0, np.nan
    for i in range(m):
        if pos == 1 and xd[i] and (cv[i] > fill or cv[i] < fill * (1 - k)):
            lx[i] = True
            pos = 0
        elif pos == 0 and ent[i] and i + 1 < m:
            le[i] = True
            pos, fill = 1, ov[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
