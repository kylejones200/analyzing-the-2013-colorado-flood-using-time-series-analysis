use analyzing_the_2013_colorado_flood_using_time_series_analysis_core::block_max;

fn main() {
    let v: Vec<f64> = (0..10000).map(|i| (i as f64 * 0.01).sin()).collect();
    for _ in 0..5000 {
        let _ = block_max(&v, 7);
    }
}
