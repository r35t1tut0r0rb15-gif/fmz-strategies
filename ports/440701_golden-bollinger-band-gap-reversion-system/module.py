"""RSI 20 crossings in quiet markets, 2-hour bars: the RSI crossing over 35 with the close under the upper band (60, 2) and the ADX under 32 goes long, crossing under 65 with the close above the upper
band short; a tight tick bracket and the close crossing the band basis close; reversing.
Port of FMZ strategy #440701 "Golden Bollinger Band Gap Reversion System" (Bollinger Bands, RSI and ADX Trading System).

FMZ source id: 440701

Source
    https://www.fmz.com/strategy/440701 (PineScript v4, FMZ last modified 2024-02-01 11:46:13).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 176-241), RSI 20 (35 / 65); BB 60 / 2; ADX 14 / 14 under 32; tp 90, sl 90 (ticks)
    longEntry = close < upper and crossover(rsi, 35) and adx < 32 -> entry long, strategy.exit(profit = 90, loss = 90), close long on crossunder(close, basis)
    shortEntry = close > upper and crossunder(rsi, 65) and adx < 32 -> entry short, the same bracket, close short on crossover(close, basis)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the 90-tick target and stop (9 USD on BTC with 0.1 ticks, about 0.03 ATR against a
      2-hour ATR near 300) become 0.03 x ATR(14) of the signal bar as fractions of its close, shifted
      one bar inside stops() and re-based on the fill; the second grid value widens them. The session
      tests are commented out. The basis closes are bar-close tests sent at the next open; a close acts
      only on the held position. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on
      2-hour bars: mark coarse_bar_stop. No sizing code. FREQ = "2h" from the backtest header (bars on UTC
      multiples of 2 hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the session filters are commented out).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440701_rsi20_quiet_band_tick_bracket"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_br": [0.03, 1.0],
    "adx_max": [32, 25],
}
DEFAULT_PARAMS = {"k_br": 0.03, "adx_max": 32, "rsi_len": 20, "oversold": 35, "overbought": 65, "bb_len": 60,
                  "bb_mult": 2.0, "adx_len": 14, "di_len": 14, "atr_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _adx(bars_df, di_len, adx_len):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, di_len)
    plus = _fixnan(100 * _rma(pdm, di_len) / trr)
    minus = _fixnan(100 * _rma(mdm, di_len) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["bb_len"])
    basis = c.rolling(n).mean()
    upper = basis + float(p["bb_mult"]) * c.rolling(n).std(ddof=0)
    adx = _adx(bars_df, int(p["di_len"]), int(p["adx_len"]))
    q = adx < float(p["adx_max"])
    os_, ob = float(p["oversold"]), float(p["overbought"])
    lsig = (c < upper) & (r > os_) & (r.shift(1) <= os_) & q
    ssig = (c > upper) & (r < ob) & (r.shift(1) >= ob) & q
    xl = (c < basis) & (c.shift(1) >= basis.shift(1))
    xs = (c > basis) & (c.shift(1) <= basis.shift(1))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    br = float(p["k_br"]) * _rma(tr, int(p["atr_len"])) / c
    return lsig.to_numpy(), ssig.to_numpy(), xl.to_numpy(), xs.to_numpy(), br


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lsig, ssig, xl, xs, br_s = _setup(bars_df, p)
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
        held = pos
        new = pos
        if lsig[i] and held != 1 and i + 1 < m and not np.isnan(br[i]):
            new, entry_i, b_ = 1, i + 1, br[i]
        if xl[i] and held == 1 and new == 1:
            new = 0
        if ssig[i] and held != -1 and i + 1 < m and not np.isnan(br[i]):
            new, entry_i, b_ = -1, i + 1, br[i]
        if xs[i] and held == -1 and new == -1:
            new = 0
        if new == 1 and held != 1:
            le[i] = True
        elif new == -1 and held != -1:
            se[i] = True
        elif new == 0 and held == 1:
            lx[i] = True
        elif new == 0 and held == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    br = _setup(bars_df, p)[4].shift(1)
    return {"sl_stop": br, "tp_stop": br.copy()}


def portfolio_kwargs(**params):
    return {}
