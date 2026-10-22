"""Three-timeframe Ichimoku, MACD and DMI agreement, 1-hour bars: the close above the 15-minute, 1-hour and 4-hour Senkou A with the 1-hour MACD above its signal and zero, the 1-hour and 15-minute
+DI above -DI with both ADX at or above 25 and the 15-minute MACD above zero goes long; the mirror goes short; reversing.
Port of FMZ strategy #440878 "基于多时间框架的一云延伸MACD和DMI组合策略Multi-Timeframe-Ichimoku-MACD-and-DMI-Combined-Strategy" (Ichimoku, MACD, DMI Multiple time frame 21/01/2024).

FMZ source id: 440878

Source
    https://www.fmz.com/strategy/440878 (PineScript v5, FMZ last modified 2024-02-02 18:04:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 159-239), timeframes 5 / 15 / 60 / 240 minutes; Ichimoku 9 / 26 / 52; MACD 12 / 26 / 9; DMI 14; ADX level 25 (the 20 input is unused)
    buyH1 = close > spanA(M15) and close > spanA(H1) and close > spanA(H4) and macdH1 > signalH1 and macdH1 > 0 and signalH1 > 0 and plusH1 > minusH1 and adxH1 >= 25
    buyM15 = the three spans and macdM15 > 0 and plusM15 > minusM15 and adxM15 >= 25;  buy = buyH1 and buyM15 -> entry Buy;  sell mirrored -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-5 request.security() without lookahead: the 15-minute values requested from the 1-hour
      chart are those of the last 15-minute bar inside the chart bar (a lower time frame returns its last
      bar, as #436765); the 4-hour values are those of the last completed 4-hour bar (UTC multiples);
      both are built from the loader's minutes. The 60-minute request is the chart itself; the 5-minute
      values are unused. The ADX threshold input (20) is not used; the code tests 25. strategy.entry
      reverses: REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; 15-minute values end with the chart bar, 4-hour values from completed bars.
    2 generic: PASS, Ichimoku span, MACD and DMI on three timeframes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_440878_three_tf_ichimoku_macd_dmi"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_min": [25, 20],
    "length_dmi": [14, 7],
}
DEFAULT_PARAMS = {"adx_min": 25, "length_dmi": 14}


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
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _span_a(b):
    h, lo = b["high"], b["low"]
    tk = (h.rolling(9).max() + lo.rolling(9).min()) / 2
    kj = (h.rolling(26).max() + lo.rolling(26).min()) / 2
    return (tk + kj) / 2


def _macd(c):
    m = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    return m, m.ewm(span=9, adjust=False).mean()


def _dmi(b, n):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), n)
    return plus, minus, adx


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["length_dmi"])
    bars = _resample(raw_1m_df, FREQ)
    b15 = _resample(raw_1m_df, "15min")
    m15, _ = _macd(b15["close"])
    p15, n15, a15 = _dmi(b15, n)
    f15 = pd.DataFrame({"s15a": _span_a(b15), "m15": m15, "p15": p15, "n15": n15, "a15": a15})
    lab = b15.index.floor(FREQ)
    last = ~pd.Index(lab).duplicated(keep="last")         # the last 15-minute bar inside each 1-hour bar
    f15 = f15[last]
    f15.index = lab[last]
    bars = bars.join(f15)
    b4 = _resample(raw_1m_df, "4h")
    s4 = _span_a(b4).shift(1)                              # the last completed 4-hour bar
    bars["s4a"] = s4.reindex(bars.index.floor("4h")).to_numpy()
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    s1 = _span_a(bars_df)
    mh, sh = _macd(c)
    ph, nh, ah = _dmi(bars_df, int(p["length_dmi"]))
    s15, s4 = bars_df["s15a"], bars_df["s4a"]
    m15, p15, n15, a15 = bars_df["m15"], bars_df["p15"], bars_df["n15"], bars_df["a15"]
    am = float(p["adx_min"])
    up_all = (c > s15) & (c > s1) & (c > s4)
    dn_all = (c < s15) & (c < s1) & (c < s4)
    buy = (up_all & (mh > sh) & (mh > 0) & (sh > 0) & (ph > nh) & (ah >= am)
           & (m15 > 0) & (p15 > n15) & (a15 >= am))
    sell = (dn_all & (mh < sh) & (mh < 0) & (sh < 0) & (nh > ph) & (ah >= am)
            & (m15 < 0) & (n15 > p15) & (a15 >= am))
    false = pd.Series(False, index=c.index)
    return buy, false, sell, false.copy()


def portfolio_kwargs(**params):
    return {}
