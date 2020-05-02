## Development log

### Variables that should be added to Picasso profiles

`atmospheric_molecular_calculation_source`: US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas
`backscatter_calibration_range_search_algorithm`: minimum_of_signal_ratio minimum_of_elastic_signal
`backscatter_calibration_search_range`:
`backscatter_evaluation_method`:
`cirrus_contamination`: 0 (because the profiles were cloud-screened first)
`cirrus_contamination_source`: 'automatic_calculated'
`cloud_mask`: 1 (unknown cloud)
`elastic_backscatter_algorithm`: 1 (iterative)
`error_retrieval_method`: 1 (error_propagation)
`raman_backscatter_algorithm`: 0 (Ansmann)
`shots`: need to be implemented (∆∆∆)
`user_defined_category`: User input
`vertical_resolution`: smoothWin * size(height) (resolution for each bin: m)
`zenith_angle`: need to be implemented (∆∆∆)
`extinction_evaluation_algorithm`: 1 (non-weighted_linear_fit)