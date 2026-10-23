"""ALMA 60 crossing ALMA 120 of the close (offset 0.85, sigma 6) with a positive volume oscillator (EMA 5 over EMA 10 of volume), entered only when flat, 4-hour bars: crossing up goes long, crossing down goes short, each with a 2 % target and a 2.5 % stop from the entry; one trade at a time.
Port of FMZ strategy #380250 "Arnaud Legoux Moving Average Cross ALMA" (ALMA Cross).

FMZ source id: 380250

Source
    https://www.fmz.com/strategy/380250 (PineScript v5, FMZ last modified 2022-08-27 17:09:42).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 48-123), ALMA 60 / 120, offset 0.85, sigma 6; volume EMA 5 / 10; TP 2 %, SL 2.5 % of the avg price
    buySignal = crossover(Alma1, Alma2) and 100 (ema(volume, 5) - ema(volume, 10)) / ema(volume, 10) > 0 and position_size == 0 -> entry Long;  sellSignal = crossunder(...) and osc > 0 and flat -> entry Short
    position_size > 0 -> exit(limit = avg x 1.02, stop = avg x 0.975);  position_size < 0 -> exit(limit = avg x 0.98, stop = avg x 1.025)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both sides need the volume oscillator above 0, as written. "Flat" follows the house bracket: the
      loop marks a trade closed when a bar reaches its stop (taken first) or its target from the fill
      price, so a new entry waits for that. The bracket is the house one from the fill bar (Pine places it
      at the close of the fill bar, so its first bar is unprotected there). The ALMA is Pine's ta.alma
      (m = 0.85 x (n - 1), s = n / 6, no floor). Stops on 4-hour bars: mark coarse_bar_stop. Stop module:
      portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, ALMA cross with a volume-oscillator filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG380250 (2 members, best partner #427669, Jaccard 0.949); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the oscillator 100 x (ema(volume, 5) - ema(volume, 10)) / ema(volume, 10) > 0; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_380250_alma60_120_cross_volume_osc_pct_bracket_flat_only"
FAMILY = "ma_crossover"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "alma1": [60, 30],
    "alma2": [120, 90],
}
DEFAULT_PARAMS = {"alma1": 60, "alma2": 120, "offset": 0.85, "sigma": 6, "shortlen": 5, "longlen": 10,
                  "tp": 0.02, "sl": 0.025}


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


def _alma(x, n, offset, sigma):
    """Pine ta.alma: Gaussian weights centred at offset x (n - 1), width n / sigma, newest bar last."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        m, s = offset * (n - 1), n / sigma
        w = np.exp(-((np.arange(n) - m) ** 2) / (2 * s * s))      # column 0 = the oldest bar
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    c, v = bars_df["close"], bars_df["volume"]
    a1 = _alma(c, int(p["alma1"]), float(p["offset"]), float(p["sigma"]))
    a2 = _alma(c, int(p["alma2"]), float(p["offset"]), float(p["sigma"]))
    es, el = v.ewm(span=int(p["shortlen"]), adjust=False).mean(), v.ewm(span=int(p["longlen"]), adjust=False).mean()
    osc = 100 * (es - el) / el
    buy = (a1 > a2) & (a1.shift(1) <= a2.shift(1)) & (osc > 0)
    sell = (a1 < a2) & (a1.shift(1) >= a2.shift(1)) & (osc > 0)
    return buy.to_numpy(), sell.to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell = _signals(bars_df, p)
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    tp, sl = float(p["tp"]), float(p["sl"])
    m = len(o)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, fill = 0, np.nan
    for i in range(m):
        if pos == 1 and (lo[i] <= fill * (1 - sl) or h[i] >= fill * (1 + tp)):
            pos = 0
        elif pos == -1 and (h[i] >= fill * (1 + sl) or lo[i] <= fill * (1 - tp)):
            pos = 0
        if pos == 0 and i + 1 < m:
            if buy[i]:
                le[i], pos, fill = True, 1, o[i + 1]
            elif sell[i]:
                se[i], pos, fill = True, -1, o[i + 1]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
