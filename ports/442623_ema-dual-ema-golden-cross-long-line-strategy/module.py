"""EMA 200 trend with an EMA 5 / 10 stack and an ATR expansion filter, 1-hour bars, long only: the close above the EMA 200, the EMA 5 above the EMA 10 and the ATR(14) above 1.5 x its average go long; a 15 %
trailing stop from the highest high and the EMA 5 crossing under the EMA 10 close.
Port of FMZ strategy #442623 "双EMA黄金交叉长线策略Dual-EMA-Golden-Cross-Long-Line-Strategy" (Strategia EMA Long con Opzioni di Uscita Avanzate).

FMZ source id: 442623

Source
    https://www.fmz.com/strategy/442623 (PineScript v5, FMZ last modified 2024-02-23 12:17:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 114-175), EMA 200 / 5 / 10; ATR 14, threshold SMA 14 x 1.5 (on); trailing stop 15 % (on); EMA cross exit (on)
    enterLong = close > ema200 and ema5 > ema10 and atr > sma(atr, 14) x 1.5 -> entry Enter Long
    in position: max high since entry;  exit(stop = max high x (1 - 15 %));  crossunder(ema5, ema10) -> close

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trailing stop is the highest high since the fill bar times 0.85, re-sent each bar: the house
      percent trail {"type": "percent", "pct": 0.15, "anchor": "high_low"} from the fill (stated
      approximation of the bar-close update; mark trailing_stop). The entry repeats while the condition
      holds and is refused while long. Long only. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: PASS, EMA trend stack with an ATR filter; percent trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_442623_ema200_stack_atr_filter_pct_trail_long"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_pct": [0.15, 0.05],
    "atr_mult": [1.5, 1.0],
}
DEFAULT_PARAMS = {"trail_pct": 0.15, "atr_mult": 1.5, "atr_len": 14, "ema_long": 200, "ema_short": 5, "ema_mid": 10}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    em = c.ewm(span=int(p["ema_mid"]), adjust=False).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    n = int(p["atr_len"])
    atr = _rma(tr, n)
    go = ((c > el) & (es > em) & (atr > atr.rolling(n).mean() * float(p["atr_mult"]))).to_numpy()
    out = ((es < em) & (es.shift(1) >= em.shift(1))).to_numpy()
    pct = float(p["trail_pct"])
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(hv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, best = 0, -1, np.nan
    for i in range(m):
        if pos == 1 and i > entry_i and lv[i] <= best * (1 - pct):
            pos = 0
        if pos == 1 and i >= entry_i and out[i]:
            lx[i], pos = True, 0
        elif pos == 0 and go[i] and i + 1 < m:
            le[i], pos, entry_i, best = True, 1, i + 1, np.nan
        if pos == 1 and i >= entry_i:
            best = hv[i] if np.isnan(best) else max(best, hv[i])
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
