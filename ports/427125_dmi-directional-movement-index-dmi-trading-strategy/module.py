"""DMI strong-up, long only: a long opens when the market turns "strong up" (ADX(14) above 25 with
+DI(7) above -DI(7)) and closes when it stops being strong up.
Port of FMZ strategy #427125 "Directional Movement Index DMI Trading Strategy".

FMZ source id: 427125

Source
    https://www.fmz.com/strategy/427125 (PineScript v5, FMZ last modified 2023-09-18 14:11:21).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 117-213), trade type 'Long', DI 7, ADX smoothing 14, level 25
    plusDM / minusDM as ta.dmi; plus = fixnan(100 rma(plusDM, 7) / rma(tr, 7)) (minus mirrors)
    adx = 100 rma(abs(plus - minus) / (plus + minus or 1), 14)
    strong_up = adx > 25 and plus > minus
    not strong_up[1] and strong_up -> entry long; strong_up[1] and not strong_up -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * trade_type is the constant 'Long' (the input is commented out): long only, as the source runs.
    * The test-date window (start / finish timestamps) is the author's backtest window: dropped.
    * fixnan carries the last non-na value forward in time (causal; a 0 / 0 when the true range
      average is 0); ta.tr is na on the first bar (ta.tr(false)), so the averages start on bar 2.
    * Entries only from flat (pyramiding 1); the close exits; one signal per bar.
    * FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (calc_on_every_tick false).
    2 generic: PASS, DI / ADX levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, commission and slippage settings stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427125_dmi_strong_up_long"
FAMILY = "directional_movement"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "di_length": [7, 14],
    "adx_smoothing": [14, 7],
    "adx_level": [25, 20],
}
DEFAULT_PARAMS = {"di_length": 7, "adx_smoothing": 14, "adx_level": 25}


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


def _fixnan(a):
    """Pine fixnan: a na value is replaced by the last earlier non-na value (causal)."""
    out = a.copy()
    last = np.nan
    for i in range(len(out)):
        if np.isnan(out[i]):
            out[i] = last
        else:
            last = out[i]
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    plus_dm = np.where(up.isna(), np.nan, np.where((up > dn) & (up > 0), up, 0.0))
    minus_dm = np.where(dn.isna(), np.nan, np.where((dn > up) & (dn > 0), dn, 0.0))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    n = int(p["di_length"])
    trr = _rma(tr, n).to_numpy()
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = _fixnan(np.where(trr == 0, np.nan, 100 * _rma(pd.Series(plus_dm, index=c.index), n).to_numpy() / trr))
        minus = _fixnan(np.where(trr == 0, np.nan, 100 * _rma(pd.Series(minus_dm, index=c.index), n).to_numpy() / trr))
        s = plus + minus
        dx = np.abs(plus - minus) / np.where(s == 0, 1.0, s)
    adx = 100 * _rma(pd.Series(dx, index=c.index), int(p["adx_smoothing"])).to_numpy()
    strong = (adx > p["adx_level"]) & (plus > minus)
    prev = np.concatenate(([False], strong[:-1]))
    entry, exit_ = strong & ~prev, prev & ~strong
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        if pos == 0 and entry[i]:
            le[i], pos = True, 1
        elif pos == 1 and exit_[i]:
            lx[i], pos = True, 0
    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), pd.Series(lx, index=idx), false.copy(), false.copy()


def portfolio_kwargs(**params):
    return {}
