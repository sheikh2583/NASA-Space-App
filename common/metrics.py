"""Agreement and interval metrics used in every validation piece."""
from __future__ import annotations

import numpy as np
from scipy import stats


def _arr(*xs):
    out = [np.asarray(x, dtype=float) for x in xs]
    ok = np.ones(out[0].shape, dtype=bool)
    for a in out:
        ok &= ~np.isnan(a)
    return [a[ok] for a in out]


def relative_bias(y_true, y_pred) -> float:
    """Signed (sum pred - sum true) / sum true."""
    t, p = _arr(y_true, y_pred)
    return float((p.sum() - t.sum()) / t.sum()) if t.sum() > 0 else float("nan")


def rmse_log1p(y_true, y_pred) -> float:
    t, p = _arr(y_true, y_pred)
    return float(np.sqrt(np.mean((np.log1p(np.clip(p, 0, None)) - np.log1p(t)) ** 2))) if t.size else float("nan")


def spearman(y_true, y_pred) -> float:
    t, p = _arr(y_true, y_pred)
    if t.size < 3 or np.all(t == t[0]) or np.all(p == p[0]):
        return float("nan")
    return float(stats.spearmanr(t, p).statistic)


def lins_ccc(y_true, y_pred) -> float:
    """Lin's concordance correlation coefficient."""
    t, p = _arr(y_true, y_pred)
    if t.size < 2:
        return float("nan")
    mt, mp = t.mean(), p.mean()
    cov = np.mean((t - mt) * (p - mp))
    return float(2 * cov / (t.var() + p.var() + (mt - mp) ** 2))


def coverage(y_true, lo, hi) -> float:
    t, l, h = _arr(y_true, lo, hi)
    return float(np.mean((t >= l) & (t <= h))) if t.size else float("nan")


def interval_score(y_true, lo, hi, alpha: float = 0.1) -> float:
    """Winkler interval score (lower is better)."""
    t, l, h = _arr(y_true, lo, hi)
    s = (h - l) + (2 / alpha) * (l - t) * (t < l) + (2 / alpha) * (t - h) * (t > h)
    return float(np.mean(s)) if t.size else float("nan")


def summary(y_true, y_pred) -> dict:
    return {"rel_bias": relative_bias(y_true, y_pred), "rmse_log1p": rmse_log1p(y_true, y_pred),
            "spearman": spearman(y_true, y_pred), "lins_ccc": lins_ccc(y_true, y_pred),
            "n": int(np.sum(~np.isnan(np.asarray(y_true, dtype=float))))}
