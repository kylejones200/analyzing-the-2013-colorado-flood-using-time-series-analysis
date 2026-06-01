//! Block max aggregation (weekly max when period=7).

pub fn block_max(values: &[f64], period: usize) -> Vec<f64> {
    if period == 0 || values.is_empty() {
        return Vec::new();
    }
    let n_blocks = values.len().div_ceil(period);
    let mut out = Vec::with_capacity(n_blocks);
    for b in 0..n_blocks {
        let start = b * period;
        let end = (start + period).min(values.len());
        let mx = values[start..end]
            .iter()
            .copied()
            .fold(f64::NEG_INFINITY, f64::max);
        out.push(mx);
    }
    out
}
