"""Three-minute bars: an RSI 14 bottom (two bars back, under 30) that is higher than the previous bottom while the low made a lower low on less 3-bar volume, after a peak, goes long with a stop 2 % under the signal close; the mirror at an RSI peak over 70 goes short with a stop 2 % over; a long closes at the next bearish-divergence peak, a short at the next bullish-divergence bottom; reversing.
Port of FMZ strategy #445456 "RSI动态止损止盈策略RSI-Dynamic-Stop-Loss-and-Take-Profit-Strategy" (RMM_byMR).

FMZ source id: 445456

Source
    https://www.fmz.com/strategy/445456 (PineScript v4, FMZ last modified 2024-03-19 15:54:01).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 104-171), RSI 14, 70 / 30; stop 2 %
    isBottom = rsi[2] < 30 and rsi[2] < rsi[1] and rsi[2] < rsi[3] and (rsi[1] < rsi or rsi[3] < rsi[4]);  isBuySignal = prevBottomBar > prevPeakBar and isBottom and rsi[2] > prevBottom and low[2] < prevBottomLow and vol3 < volumeBottom -> entry Buy, exit(stop = close x 0.98)
    isBuyTakeProfit = isPeak and ((rsi[2] < prevPeak and high[2] > prevPeakHigh) or (rsi[2] < prevPeak and vol3 < volumePeak)) -> close Buy;  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * prevPeak / prevBottom and their prices, 3-bar volumes and bar indexes are the previous pivot's
      (valuewhen(..., 1)). The stops are sent on the signal bar only, as levels from that bar's close:
      fractions of the fill, exact (1e-6 floor). A sell signal is also a long take-profit bar; the close
      acts only on a position the bar's entries leave unchanged. REVERSAL INTENDED. No sizing code. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop at the signal close as a fraction of the fill.
    2 generic: PASS, RSI pivot divergences with falling volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data) as the 3-bar volume at each RSI pivot compared with the previous pivot's; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_445456_rsi_pivot_divergence_falling_volume_2pct_stop_3m_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_len": [14, 21],
    "stop_pct": [0.02, 0.01],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ob": 70.0, "os": 30.0, "stop_pct": 0.02}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _signals(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    r = _rsi(c, int(p["rsi_len"]))
    r1, r2, r3, r4 = r.shift(1), r.shift(2), r.shift(3), r.shift(4)
    peak = ((r2 > float(p["ob"])) & (r2 > r1) & (r2 > r3) & ((r1 > r) | (r3 > r4))).to_numpy()
    bott = ((r2 < float(p["os"])) & (r2 < r1) & (r2 < r3) & ((r1 < r) | (r3 < r4))).to_numpy()
    rv2, hv2, lv2 = r2.to_numpy(), h.shift(2).to_numpy(dtype=float), lo.shift(2).to_numpy(dtype=float)
    vol3 = (v.shift(1) + v.shift(2) + v.shift(3)).to_numpy(dtype=float)
    m = len(peak)
    buy, sell = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    btp, stp = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    cur_pk = prev_pk = None                             # (rsi, high, vol3, bar) of the latest / previous peak
    cur_bt = prev_bt = None
    for i in range(m):
        if peak[i]:
            prev_pk, cur_pk = cur_pk, (rv2[i], hv2[i], vol3[i], i)
        if bott[i]:
            prev_bt, cur_bt = cur_bt, (rv2[i], lv2[i], vol3[i], i)
        pk_bar = prev_pk[3] if prev_pk else np.nan
        bt_bar = prev_bt[3] if prev_bt else np.nan
        if peak[i] and prev_pk:
            pr, ph_, pvol, _ = prev_pk
            sell[i] = pk_bar > bt_bar and rv2[i] < pr and hv2[i] > ph_ and vol3[i] < pvol
            btp[i] = (rv2[i] < pr and hv2[i] > ph_) or (rv2[i] < pr and vol3[i] < pvol)
        if bott[i] and prev_bt:
            br, bl, bvol, _ = prev_bt
            buy[i] = bt_bar > pk_bar and rv2[i] > br and lv2[i] < bl and vol3[i] < bvol
            stp[i] = (rv2[i] > br and lv2[i] < bl) or (rv2[i] > br and vol3[i] < bvol)
    return buy, sell, btp, stp


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, btp, stp = _signals(bars_df, p)
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        new = pos
        if buy[i] and new != 1:
            new = 1
        if sell[i] and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and btp[i]:
                new = 0
            elif pos == -1 and stp[i]:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    k = c.shift(1) / o                                  # the signal close as a fraction of the fill
    s = float(p["stop_pct"])
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = pd.Series(np.nan, index=o.index).mask(lf, 1 - k * (1 - s)).mask(sf, k * (1 + s) - 1)
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
