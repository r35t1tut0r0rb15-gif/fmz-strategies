"""Early-trend dip buys with a 3 % bracket, 1-minute bars, long only: from flat, a close crossing over the SMA 9 while the SMA 9 is above the SMA 100 and the SMA 100 is under the SMA 200 buys; the trade has a
3 % target and a 3 % stop.
Port of FMZ strategy #437684 "Multi timeframe MA Trend Following Strategy" (Pyramiding Entry On Early Trends).

FMZ source id: 437684

Source
    https://www.fmz.com/strategy/437684 (PineScript v3, FMZ last modified 2024-01-04 17:43:17).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 145-194), SMA 9 / 100 / 200; profit 3 % / loss 3 % (as ticks of the close); pyramiding 7; date window true
    longsignal = crossover(close, sma 9) and sma 9 > sma 100 and sma 100 < sma 200;  entry "Entry 1" when opentrades == 0 (Entries 2-7 add at opentrades 1-6)
    exit(profit = close x 3 % / mintick, loss = close x 3 % / mintick) per entry, re-sent every bar while long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The adds Entry 2-7 that pyramiding 7 allows are sizing: the port holds one position, entered from
      flat. The bracket is written in ticks of 3 % of the close, re-sent each bar from that bar's close;
      the port reads it as fixed 3 % fractions of the entry fill (the moving close changes the distance
      only a little, as #437004). "Flat" follows the house bracket. Long only. Stop module: portfolio_kwargs
      {} (driver D4). The 20 % of equity size and commission are sizing. FREQ = "1min" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the entry.
    2 generic: PASS, percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: pyramiding 7, the percent-of-equity size and commission stored.
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

NAME = "fmz_437684_early_trend_dip_pct_bracket_long"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.03, 0.015],
    "sl": [0.03, 0.015],
}
DEFAULT_PARAMS = {"tp": 0.03, "sl": 0.03, "fast": 9, "slow": 100, "long": 200}


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
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    lg = c.rolling(int(p["long"])).mean()
    sig = ((c > f) & (c.shift(1) <= f.shift(1)) & (f > s) & (s < lg)).to_numpy()
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos == 1 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - sl) or hv[i] >= e * (1 + tp):
                pos = 0
        if pos == 0 and sig[i] and i + 1 < m:
            le[i] = True
            pos, entry_i = 1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
