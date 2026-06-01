use analyzing_the_2013_colorado_flood_using_time_series_analysis_core::block_max;
use numpy::{PyArray1, PyReadonlyArray1, IntoPyArray};
use pyo3::prelude::*;

#[pyfunction]
fn block_max_py<'py>(py: Python<'py>, values: PyReadonlyArray1<f64>, period: usize) -> PyResult<Bound<'py, PyArray1<f64>>> {
    Ok(block_max(values.as_slice()?, period).into_pyarray(py))
}

#[pyfunction]
#[pyo3(signature = (values, period, iterations=500))]
fn bench_kernel_py(values: PyReadonlyArray1<f64>, period: usize, iterations: usize) -> PyResult<f64> {
    let v = values.as_slice()?.to_vec();
    let start = std::time::Instant::now();
    for _ in 0..iterations {
        let _ = block_max(&v, period);
    }
    Ok(start.elapsed().as_secs_f64())
}

#[pymodule]
fn analyzing_the_2013_colorado_flood_using_time_series_analysis_rs(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(block_max_py, m)?)?;
    m.add_function(wrap_pyfunction!(bench_kernel_py, m)?)?;
    Ok(())
}
