"""DMI crossings with ADX and EMA 26 filters and one-shot state flags, 4-hour bars: +DI crossing over -DI with the ADX over 20 above the EMA goes long, -DI over +DI with the ADX over 25 under the EMA goes
short; a -DI (or +DI) cross with the ADX over 30 closes the long (short); each signal fires once per state; reversing.
Port of FMZ strategy #441958 "Overlay Trend Signals Strategy" (Overlay Signals by TFOT).

FMZ source id: 441958

Source
    https://www.fmz.com/strategy/441958 (PineScript v5, FMZ last modified 2024-02-18 10:00:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 173-248), DI 14, ADX smoothing 14; EMA 26 (seeded with the first close); labels shown
    buy = crossover(+DI, -DI) and adx > 20 and close > EMA and na(firstbuybar);  sell = crossover(-DI, +DI) and adx > 25 and close < EMA and na(firstsellbar)
    buyexit = crossover(-DI, +DI) and adx > 30 and na(buyexitbar);  sellexit = crossover(+DI, -DI) and adx > 30 and na(sellexitbar)
    buy -> firstbuybar = bar, buyexitbar = na, firstsellbar = na, entry Buy;  sell -> mirror, entry Sell;  buyexit and firstbuybar set -> buyexitbar = bar, both first bars na, close Buy;  sellexit mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags are ported as written, in call order (the conditions read the flags as they stood at the
      start of the bar; the exit checks read them after the entries). A close acts only on the held
      position. strategy.entry reverses: REVERSAL INTENDED. No sizing code. FREQ = "4h" from the backtest
      header (bars on UTC multiples of 4 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, DMI crossings with ADX / EMA filters and state flags.
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

NAME = "fmz_441958_dmi_cross_adx_ema_flag_state"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "di_len": [14, 21],
    "ema_len": [26, 50],
}
DEFAULT_PARAMS = {"di_len": 14, "ema_len": 26}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    dp, dm, adx = _dmi(bars_df, int(p["di_len"]))
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    xpm = ((dp > dm) & (dp.shift(1) <= dm.shift(1))).to_numpy()
    xmp = ((dm > dp) & (dm.shift(1) <= dp.shift(1))).to_numpy()
    av = adx.to_numpy()
    above, below = (c > ema).to_numpy(), (c < ema).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    fb = fs = bx = sxb = None
    held = 0
    for i in range(m):
        b1 = xpm[i] and av[i] > 20 and above[i] and fb is None
        s1 = xmp[i] and av[i] > 25 and below[i] and fs is None
        bx1 = xmp[i] and av[i] > 30 and bx is None
        sx1 = xpm[i] and av[i] > 30 and sxb is None
        new = held
        if b1:
            fb, bx, fs = i, None, None
            if new != 1:
                new = 1
        if s1:
            fs, sxb, fb = i, None, None
            if new != -1:
                new = -1
        if bx1 and fb is not None:
            bx, fb, fs = i, None, None
            if held == 1 and new == 1:
                new = 0
        if sx1 and fs is not None:
            sxb, fs, fb = i, None, None
            if held == -1 and new == -1:
                new = 0
        tgt[i] = new
        held = new
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
