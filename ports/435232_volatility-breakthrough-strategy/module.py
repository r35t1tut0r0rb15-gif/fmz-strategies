"""Four-condition trend state, 10-minute bars: a close above the SMA 48 and the Bollinger 20 basis with a positive MACD
histogram and ADX 14 above 25 goes (or stays) long; the mirror goes short (reversing); held otherwise.
Port of FMZ strategy #435232 "Volatility Breakthrough Strategy" (Volatility Traders Minds Strategy (VTM Strategy)).

FMZ source id: 435232

Source
    https://www.fmz.com/strategy/435232 (PineScript v4, FMZ last modified 2023-12-13 14:36:04).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 182-280), SMA 48; MACD 12 / 26 / 9; BB 20 x 2 basis; ADX 14 / 14 > 25; TP / SL / trail 0 (off); custom dates off
    close > sma48 and close > basis and delta > 0 and adx > 25 -> entry long;  close < sma48 and close < basis and delta < 0 and adx > 25 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * All risk inputs are 0, so the exits are never armed: dropped. strategy.entry reverses: REVERSAL
      INTENDED. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, averages, MACD and ADX states.
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

NAME = "fmz_435232_vtm_four_condition_state"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_len": [48, 100],
    "adx_th": [25, 20],
}
DEFAULT_PARAMS = {"ma_len": 48, "bb_len": 20, "adx_th": 25, "adx_len": 14, "di_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v, index):
    """Pine fixnan: a NaN (or inf) takes the last valid value before it (past values only)."""
    out = np.array(v, dtype=float)
    last = np.nan
    for i in range(len(out)):
        if np.isfinite(out[i]):
            last = out[i]
        else:
            out[i] = last
    return pd.Series(out, index=index)


def _adx(h, lo, c, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    rma = lambda x, n: x.ewm(alpha=1 / n, adjust=False).mean()  # noqa: E731
    trur = rma(tr, di_len)
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    plus = _fixnan((100 * rma(pdm, di_len) / trur).to_numpy(), c.index)
    minus = _fixnan((100 * rma(ndm, di_len) / trur).to_numpy(), c.index)
    s = plus + minus
    return 100 * rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma = c.rolling(int(p["ma_len"])).mean()
    basis = c.rolling(int(p["bb_len"])).mean()
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    delta = macd - macd.ewm(span=9, adjust=False).mean()
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    ok = adx > float(p["adx_th"])
    up = ((c > ma) & (c > basis) & (delta > 0) & ok).to_numpy()
    dn = ((c < ma) & (c < basis) & (delta < 0) & ok).to_numpy()
    m = len(up)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if up[i]:
            q = 1
        elif dn[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
