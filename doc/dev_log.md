## Development log

### Variables that should be added to Picasso profiles

- [x] `atmospheric_molecular_calculation_source`: US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas (∆∆∆)
- [x] `backscatter_calibration_range_search_algorithm`: minimum_of_signal_ratio minimum_of_elastic_signal
- [x] `backscatter_calibration_search_range`: (∆∆∆)
- [x] `backscatter_calibration_range`: (∆∆∆)
- [x] `backscatter_evaluation_method`:
- [x] `cirrus_contamination`: 0 (because the profiles were cloud-screened first)
- [x] `cirrus_contamination_source`: 'automatic_calculated'
- [x] `cloud_mask`: 1 (unknown cloud)
- [x] `elastic_backscatter_algorithm`: 1 (iterative)
- [x] `error_retrieval_method`: 1 (error_propagation)
- [x] `raman_backscatter_algorithm`: 0 (Ansmann)
- [x] `shots`: need to be implemented (∆∆∆)
- [x] `user_defined_category`: User input
- [x] `vertical_resolution`: smoothWin * size(height) (resolution for each bin: m) (∆∆∆)
- [x] `zenith_angle`: need to be implemented (∆∆∆)
- [x] `extinction_evaluation_algorithm`: 1 (non-weighted_linear_fit)
- [ ] uncertainty of extinction and backscatter
