"""Triple-average pull-back bounces, 2-hour bars: with SMMA 10 above EMA 55 above SMA 110, a dip of the low under the EMA two bars back after a low above it five bars back, with the previous close back
above it, goes long from flat (mirrored for shorts); a 2 ATR(12) target and stop from the signal close; the SMMA crossing the SMA closes.
Port of FMZ strategy #440862 "Dazzling Bolts Trend Following Strategy" (Dazzling Bolts).

FMZ source id: 440862

Source
    https://www.fmz.com/strategy/440862 (PineScript v4, FMZ last modified 2024-02-02 17:30:09).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 161-213), SMMA 10, EMA 55, SMA 110; force trend with EMA 6 bars back on; longs and shorts on; ATR 12 x 2
    bullbounce = smma > ema > sma and low[5] > ema and low[2] < ema and close[1] > ema and ema[6] > sma;  bullbuy = bullbounce and opentrades == 0 -> entry Boltsup, strategy.exit(limit = close + 2 atr, stop = close - 2 atr)
    crossover(smma, sma) -> close Boltsup;  shorts mirrored (crossunder(smma, sma) -> close Boltsdown)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set once on the signal bar from its close: sl_stop = tp_stop = 2 ATR / close of the
      signal bar, shifted one bar inside stops() and re-based on the fill. As written a long closes when
      the SMMA crosses OVER the SMA (and a short when it crosses under). Entries only from flat.
      Opposite entries cannot occur (entries only from flat). Stop module: portfolio_kwargs {} (driver
      D4). Stops on 2-hour bars: mark coarse_bar_stop. The order size (capital / close) is sizing. FREQ =
      "2h" from the backtest header (bars on UTC multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, moving-average stack and ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: order size from the initial capital is sizing.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440862_dazzling_bolts_bounce_bracket"
FAMILY = "ma_pullback"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "atrm": [2.0, 1.0],
    "emalength": [55, 34],
}
DEFAULT_PARAMS = {"atrm": 2.0, "emalength": 55, "smma_len": 10, "smalength": 110, "offset": 6, "atrlength": 12}


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


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    smma = _rma(c, int(p["smma_len"]))
    ema = c.ewm(span=int(p["emalength"]), adjust=False).mean()
    sma = c.rolling(int(p["smalength"])).mean()
    k = int(p["offset"])
    bull = ((smma > ema) & (ema > sma) & (lo.shift(5) > ema) & (lo.shift(2) < ema) & (c.shift(1) > ema)
            & (ema.shift(k) > sma))
    bear = ((smma < ema) & (ema < sma) & (h.shift(5) < ema) & (h.shift(2) > ema) & (c.shift(1) < ema)
            & (ema.shift(k) < sma))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    br = float(p["atrm"]) * _rma(tr, int(p["atrlength"])) / c
    x_up = ((smma > sma) & (smma.shift(1) <= sma.shift(1))).to_numpy()
    x_dn = ((smma < sma) & (smma.shift(1) >= sma.shift(1))).to_numpy()
    return bull.to_numpy(), bear.to_numpy(), br, x_up, x_dn


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    bull, bear, br_s, x_up, x_dn = _setup(bars_df, p)
    br = br_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, b_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if hv[i] >= x * (1 + b_) or lv[i] <= x * (1 - b_):
                pos = 0
        if pos == 1 and i >= entry_i and x_up[i]:
            lx[i], pos = True, 0
            continue
        if pos == -1 and i >= entry_i and x_dn[i]:
            sx[i], pos = True, 0
            continue
        if pos == 0 and i + 1 < m and not np.isnan(br[i]):
            if bull[i]:
                le[i], pos, entry_i, b_ = True, 1, i + 1, br[i]
            elif bear[i]:
                se[i], pos, entry_i, b_ = True, -1, i + 1, br[i]
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    br = _setup(bars_df, p)[2].shift(1)
    return {"sl_stop": br, "tp_stop": br.copy()}


def portfolio_kwargs(**params):
    return {}
