# New EARLINET data format

## e355

```text
dimensions:
    altitude = 245;
    time = 1;
    wavelength = 1;
    nv = 2;

variables:
    double altitude(altitude);
        string altitude:long_name = "height above sea level";
        string altitude:units = "m";
        string altitude:axis = "Z";
        string altitude:positive = "up";
        string altitude:standard_name = "altitude";

    double time(time);
        string time:long_name = "time";
        string time:units = "seconds since 1970-01-01T00:00:00Z";
        string time:axis = "T";
        string time:standard_name = "time";
        string time:bounds = "time_bounds";
        string time:calendar = "gregorian";

    double time_bounds(time, nv);

    double vertical_resolution(wavelength, time, altitude);
        vertical_resolution:_FillValue = 9.969209968386869E36;
        string vertical_resolution:long_name = "effective vertical resolution according to Pappalardo et al., appl. opt. 2004";
        string vertical_resolution:units = "m";

    byte cloud_mask(time, altitude);
        cloud_mask:_FillValue = -127B;
        string cloud_mask:long_name = "cloud mask";
        string cloud_mask:units = "1";
        cloud_mask:flag_masks = 1B, 2B, 4B;
        string cloud_mask:flag_meanings = "unknown_cloud cirrus_cloud water_cloud";
        cloud_mask:valid_range = 0B, 7B;

    byte cirrus_contamination;
        cirrus_contamination:_FillValue = -127B;
        string cirrus_contamination:long_name = "do the profiles contain cirrus layers?";
        cirrus_contamination:flag_values = 0B, 1B, 2B;
        string cirrus_contamination:flag_meanings = "not_available no_cirrus cirrus_detected";

    byte error_retrieval_method(wavelength);
        error_retrieval_method:_FillValue = -127B;
        string error_retrieval_method:long_name = "method used for the retrieval of uncertainties";
        error_retrieval_method:flag_values = 0B, 1B;
        string error_retrieval_method:flag_meanings = "monte_carlo error_propagation";

    byte extinction_evaluation_algorithm(wavelength);
        extinction_evaluation_algorithm:_FillValue = -127B;
        string extinction_evaluation_algorithm:long_name = "algorithm used for the extinction retrieval";
        extinction_evaluation_algorithm:flag_values = 0B, 1B;
        string extinction_evaluation_algorithm:flag_meanings = "weighted_linear_fit non-weighted_linear_fit";

    double extinction(wavelength, time, altitude);
        extinction:_FillValue = 9.969209968386869E36;
        string extinction:long_name = "aerosol extinction coefficient";
        string extinction:ancillary_variables = "error_extinction vertical_resolution";
        string extinction:coordinates = "longitude latitude";
        string extinction:units = "1/m";

    double error_extinction(wavelength, time, altitude);
        error_extinction:_FillValue = 9.969209968386869E36;
        string error_extinction:long_name = "absolute statistical uncertainty of extinction";
        string error_extinction:units = "1/m";
        string error_extinction:coordinates = "longitude latitude";

    int user_defined_category;
        user_defined_category:_FillValue = -2147483647;
        string user_defined_category:long_name = "user defined category of the measurement";
        string user_defined_category:comment = "Those flags might have not been set in a homogeneous way. Before using them, contact the originator to obtain more detailed information on how these flags have been set.";
        user_defined_category:flag_masks = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512;
        string user_defined_category:flag_meanings = "cirrus climatol dicycles etna forfires photosmog rurban sahadust stratos satellite_overpasses";
        user_defined_category:valid_range = 0, 1023;

    byte cirrus_contamination_source;
        cirrus_contamination_source:_FillValue = -127B;
        string cirrus_contamination_source:long_name = "how was cirrus_contamination obtained?";
        cirrus_contamination_source:flag_values = 0B, 1B, 2B;
        string cirrus_contamination_source:flag_meanings = "not_available user_provided automatic_calculated";

    byte atmospheric_molecular_calculation_source;
        atmospheric_molecular_calculation_source:_FillValue = -127B;
        string atmospheric_molecular_calculation_source:long_name = "data source of the atmospheric molecular calculations";
        atmospheric_molecular_calculation_source:flag_values = 0B, 1B, 2B, 3B, 4B;
        string atmospheric_molecular_calculation_source:flag_meanings = "US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas";

    float latitude;
        string latitude:standard_name = "latitude";
        string latitude:long_name = "latitude of station";
        string latitude:units = "degrees_north";

    float longitude;
        string longitude:long_name = "longitude of station";
        string longitude:units = "degrees_east";
        string longitude:standard_name = "longitude";

    float station_altitude;
        station_altitude:_FillValue = 9.96921E36f;
        string station_altitude:long_name = "station altitude above sea level";
        string station_altitude:units = "m";

    float extinction_assumed_wavelength_dependence(wavelength);
        extinction_assumed_wavelength_dependence:_FillValue = 9.96921E36f;
        string extinction_assumed_wavelength_dependence:long_name = "assumed wavelength dependence for extinction retrieval";
        string extinction_assumed_wavelength_dependence:units = "1";

    float wavelength(wavelength);
        string wavelength:long_name = "wavelength of the transmitted laser pulse";
        string wavelength:units = "nm";

    float zenith_angle;
        zenith_angle:_FillValue = 9.96921E36f;
        string zenith_angle:long_name = "laser pointing angle with respect to the zenith";
        string zenith_angle:units = "degrees";

    int shots;
        shots:_FillValue = -2147483647;
        string shots:long_name = "accumulated laser shots";
        string shots:units = "1";

    int earlinet_product_type;
        earlinet_product_type:_FillValue = -2147483647;
        string earlinet_product_type:long_name = "Earlinet product type";
        earlinet_product_type:flag_values = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14;
        string earlinet_product_type:flag_meanings = "e0355 b0355 e0351 b0351 e0532 b0532 e1064 b1064 b0253 b0313 b0335 b0510 b0694 b0817";
        earlinet_product_type:valid_range = 1, 14;

    double backscatter(wavelength, time, altitude);
        backscatter:_FillValue = 9.969209968386869E36;
        string backscatter:long_name = "aerosol backscatter coefficient";
        string backscatter:units = "1/(m*sr)";
        string backscatter:ancillary_variables = "error_backscatter vertical_resolution";
        string backscatter:coordinates = "longitude latitude";

    double error_backscatter(wavelength, time, altitude);
        error_backscatter:_FillValue = 9.969209968386869E36;
        string error_backscatter:long_name = "absolute statistical uncertainty of backscatter";
        string error_backscatter:units = "1/(m*sr)";
        string error_backscatter:coordinates = "longitude latitude";

    byte backscatter_calibration_range_search_algorithm(wavelength);
        backscatter_calibration_range_search_algorithm:_FillValue = -127B;
        string backscatter_calibration_range_search_algorithm:long_name = "algorithm used for the search of the calibration_range";
        backscatter_calibration_range_search_algorithm:flag_values = 0B, 1B;
        string backscatter_calibration_range_search_algorithm:flag_meanings = "minimum_of_signal_ratio minimum_of_elastic_signal";

    float backscatter_calibration_range(wavelength, nv);
        backscatter_calibration_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_range:long_name = "height range where calibration was calculated";
        string backscatter_calibration_range:units = "m";

    byte backscatter_evaluation_method(wavelength);
        backscatter_evaluation_method:_FillValue = -127B;
        string backscatter_evaluation_method:long_name = "method used for the backscatter retrieval";
        backscatter_evaluation_method:flag_values = 0B, 1B;
        string backscatter_evaluation_method:flag_meanings = "Raman elastic_backscatter";

    byte raman_backscatter_algorithm(wavelength);
        raman_backscatter_algorithm:_FillValue = -127B;
        string raman_backscatter_algorithm:long_name = "algorithm used for the retrieval of the Raman backscatter profile";
        raman_backscatter_algorithm:flag_values = 0B, 1B;
        string raman_backscatter_algorithm:flag_meanings = "Ansmann via_backscatter_ratio";

    float backscatter_calibration_value(wavelength);
        backscatter_calibration_value:_FillValue = 9.96921E36f;
        string backscatter_calibration_value:long_name = "assumed backscatter-ratio value (unitless) in calibration range";
        string backscatter_calibration_value:units = "1";

    float backscatter_calibration_search_range(wavelength, nv);
        backscatter_calibration_search_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_search_range:long_name = "height range wherein calibration range is searched";
        string backscatter_calibration_search_range:units = "m";

// global attributes:
string :measurement_ID = "20120710po00";
string :system = "MUSA";
string :institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA), Potenza - CNR-IMAA";
string :location = "Potenza, Italy";
string :station_ID = "pot";
string :PI = "Aldo Amodeo";
string :PI_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale ";
string :PI_affiliation_acronym = "CNR-IMAA";
string :PI_address = "Contrada S.Loja, Zona Industriale - Tito Scalo I-85050 Potenza";
string :PI_phone = "+39 0971 427263";
string :PI_email = "aldo.amodeo@imaa.cnr.it";
string :Data_Originator = "damico";
string :Data_Originator_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale";
string :Data_Originator_affiliation_acronym = "CNR-IMAA";
string :Data_Originator_address = "C.da S. Loja - Zona Industriale, 85050 Potenza, Italy";
string :Data_Originator_phone = "+39 0971 427297";
string :Data_Originator_email = "giuseppe.damico@imaa.cnr.it";
string :data_processing_institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA)";
string :comment = "charmex pre-campaign";
string :scc_version = "5.1.0";
string :scc_version_description = "SCC vers. 5.1.0 (HiRELPP vers. 1.0.6, CloudMask vers. 1.1.8, ELPP vers. 7.0.5, ELDA vers. 3.3.9, ELIC vers. 1.0.3, ELQUICK vers. 1.0.3, ELDEC vers. 2.0.1)";
string :processor_name = "ELDA";
string :processor_version = "3.3.9";
string :history = "2019-06-05T17:32:11Z: elpp -d sccoperational -m 20120710po00 -c elpp.config; 2019-06-05T18:47:25Z: elda 20120710po00 -c elda.ini";
string :title = "Profiles of aerosol optical properties";
string :source = "Ground based LIDAR measurements";
string :references = "Project website at http://www.earlinet.org";
string :__file_format_version = "2.0";
string :Conventions = "CF-1.7";
:hoi_system_ID = 74;
:hoi_configuration_ID = 124;
string :input_file = "20120710po00_0000470.nc";
string :measurement_start_datetime = "2012-07-09T22:59:39Z";
string :measurement_stop_datetime = "2012-07-09T23:59:26Z";
```

## b355

```text
dimensions:
    altitude = 245;
    time = 1;
    wavelength = 1;
    nv = 2;

variables:
    double altitude(altitude);
        string altitude:long_name = "height above sea level";
        string altitude:units = "m";
        string altitude:axis = "Z";
        string altitude:positive = "up";
        string altitude:standard_name = "altitude";

    double time(time);
        string time:long_name = "time";
        string time:units = "seconds since 1970-01-01T00:00:00Z";
        string time:axis = "T";
        string time:standard_name = "time";
        string time:bounds = "time_bounds";
        string time:calendar = "gregorian";

    double time_bounds(time, nv);

    double vertical_resolution(wavelength, time, altitude);
        vertical_resolution:_FillValue = 9.969209968386869E36;
        string vertical_resolution:long_name = "effective vertical resolution according to Pappalardo et al., appl. opt. 2004";
        string vertical_resolution:units = "m";

    byte cloud_mask(time, altitude);
        cloud_mask:_FillValue = -127B;
        string cloud_mask:long_name = "cloud mask";
        string cloud_mask:units = "1";
        cloud_mask:flag_masks = 1B, 2B, 4B;
        string cloud_mask:flag_meanings = "unknown_cloud cirrus_cloud water_cloud";
        cloud_mask:valid_range = 0B, 7B;

    byte cirrus_contamination;
        cirrus_contamination:_FillValue = -127B;
        string cirrus_contamination:long_name = "do the profiles contain cirrus layers?";
        cirrus_contamination:flag_values = 0B, 1B, 2B;
        string cirrus_contamination:flag_meanings = "not_available no_cirrus cirrus_detected";

    byte error_retrieval_method(wavelength);
        error_retrieval_method:_FillValue = -127B;
        string error_retrieval_method:long_name = "method used for the retrieval of uncertainties";
        error_retrieval_method:flag_values = 0B, 1B;
        string error_retrieval_method:flag_meanings = "monte_carlo error_propagation";

    byte backscatter_evaluation_method(wavelength);
        backscatter_evaluation_method:_FillValue = -127B;
        string backscatter_evaluation_method:long_name = "method used for the backscatter retrieval";
        backscatter_evaluation_method:flag_values = 0B, 1B;
        string backscatter_evaluation_method:flag_meanings = "Raman elastic_backscatter";

    byte raman_backscatter_algorithm(wavelength);
        raman_backscatter_algorithm:_FillValue = -127B;
        string raman_backscatter_algorithm:long_name = "algorithm used for the retrieval of the Raman backscatter profile";
        raman_backscatter_algorithm:flag_values = 0B, 1B;
        string raman_backscatter_algorithm:flag_meanings = "Ansmann via_backscatter_ratio";

    double backscatter(wavelength, time, altitude);
        backscatter:_FillValue = 9.969209968386869E36;
        string backscatter:long_name = "aerosol backscatter coefficient";
        string backscatter:units = "1/(m*sr)";
        string backscatter:ancillary_variables = "error_backscatter vertical_resolution";
        string backscatter:coordinates = "longitude latitude";

    double error_backscatter(wavelength, time, altitude);
        error_backscatter:_FillValue = 9.969209968386869E36;
        string error_backscatter:long_name = "absolute statistical uncertainty of backscatter";
        string error_backscatter:units = "1/(m*sr)";
        string error_backscatter:coordinates = "longitude latitude";

    int user_defined_category;
        user_defined_category:_FillValue = -2147483647;
        string user_defined_category:long_name = "user defined category of the measurement";
        string user_defined_category:comment = "Those flags might have not been set in a homogeneous way. Before using them, contact the originator to obtain more detailed information on how these flags have been set.";
        user_defined_category:flag_masks = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512;
        string user_defined_category:flag_meanings = "cirrus climatol dicycles etna forfires photosmog rurban sahadust stratos satellite_overpasses";
        user_defined_category:valid_range = 0, 1023;

    byte cirrus_contamination_source;
        cirrus_contamination_source:_FillValue = -127B;
        string cirrus_contamination_source:long_name = "how was cirrus_contamination obtained?";
        cirrus_contamination_source:flag_values = 0B, 1B, 2B;
        string cirrus_contamination_source:flag_meanings = "not_available user_provided automatic_calculated";

    byte atmospheric_molecular_calculation_source;
        atmospheric_molecular_calculation_source:_FillValue = -127B;
        string atmospheric_molecular_calculation_source:long_name = "data source of the atmospheric molecular calculations";
        atmospheric_molecular_calculation_source:flag_values = 0B, 1B, 2B, 3B, 4B;
        string atmospheric_molecular_calculation_source:flag_meanings = "US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas";

    float latitude;
        string latitude:long_name = "latitude of station";
        string latitude:units = "degrees_north";
        string latitude:standard_name = "latitude";

    float longitude;
        string longitude:long_name = "longitude of station";
        string longitude:units = "degrees_east";
        string longitude:standard_name = "longitude";

    float station_altitude;
        station_altitude:_FillValue = 9.96921E36f;
        string station_altitude:long_name = "station altitude above sea level";
        string station_altitude:units = "m";

    float backscatter_calibration_value(wavelength);
        backscatter_calibration_value:_FillValue = 9.96921E36f;
        string backscatter_calibration_value:long_name = "assumed backscatter-ratio value (unitless) in calibration range";
        string backscatter_calibration_value:units = "1";

    float backscatter_calibration_search_range(wavelength, nv);
        backscatter_calibration_search_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_search_range:long_name = "height range wherein calibration range is searched";
        string backscatter_calibration_search_range:units = "m";

    float wavelength(wavelength);
        string wavelength:long_name = "wavelength of the transmitted laser pulse";
        string wavelength:units = "nm";

    float zenith_angle;
        zenith_angle:_FillValue = 9.96921E36f;
        string zenith_angle:long_name = "laser pointing angle with respect to the zenith";
        string zenith_angle:units = "degrees";

    int shots;
        shots:_FillValue = -2147483647;
        string shots:long_name = "accumulated laser shots";
        string shots:units = "1";

    int earlinet_product_type;
        earlinet_product_type:_FillValue = -2147483647;
        string earlinet_product_type:long_name = "Earlinet product type";
        earlinet_product_type:flag_values = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14;
        string earlinet_product_type:flag_meanings = "e0355 b0355 e0351 b0351 e0532 b0532 e1064 b1064 b0253 b0313 b0335 b0510 b0694 b0817";
        earlinet_product_type:valid_range = 1, 14;

    byte backscatter_calibration_range_search_algorithm(wavelength);
        backscatter_calibration_range_search_algorithm:_FillValue = -127B;
        string backscatter_calibration_range_search_algorithm:long_name = "algorithm used for the search of the calibration_range";
        backscatter_calibration_range_search_algorithm:flag_values = 0B, 1B;
        string backscatter_calibration_range_search_algorithm:flag_meanings = "minimum_of_signal_ratio minimum_of_elastic_signal";

    float backscatter_calibration_range(wavelength, nv);
        string backscatter_calibration_range:long_name = "height range where calibration was calculated";
        string backscatter_calibration_range:units = "m";
        backscatter_calibration_range:_FillValue = 9.96921E36f;

// global attributes:
string :measurement_ID = "20120710po00";
string :system = "MUSA";
string :institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA), Potenza - CNR-IMAA";
string :location = "Potenza, Italy";
string :station_ID = "pot";
string :PI = "Aldo Amodeo";
string :PI_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale ";
string :PI_affiliation_acronym = "CNR-IMAA";
string :PI_address = "Contrada S.Loja, Zona Industriale - Tito Scalo I-85050 Potenza";
string :PI_phone = "+39 0971 427263";
string :PI_email = "aldo.amodeo@imaa.cnr.it";
string :Data_Originator = "damico";
string :Data_Originator_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale";
string :Data_Originator_affiliation_acronym = "CNR-IMAA";
string :Data_Originator_address = "C.da S. Loja - Zona Industriale, 85050 Potenza, Italy";
string :Data_Originator_phone = "+39 0971 427297";
string :Data_Originator_email = "giuseppe.damico@imaa.cnr.it";
string :data_processing_institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA)";
string :comment = "charmex pre-campaign";
string :scc_version = "5.1.0";
string :scc_version_description = "SCC vers. 5.1.0 (HiRELPP vers. 1.0.6, CloudMask vers. 1.1.8, ELPP vers. 7.0.5, ELDA vers. 3.3.9, ELIC vers. 1.0.3, ELQUICK vers. 1.0.3, ELDEC vers. 2.0.1)";
string :processor_name = "ELDA";
string :processor_version = "3.3.9";
string :history = "2019-06-05T17:32:09Z: elpp -d sccoperational -m 20120710po00 -c elpp.config; 2019-06-05T18:47:25Z: elda 20120710po00 -c elda.ini";
string :title = "Profiles of aerosol optical properties";
string :source = "Ground based LIDAR measurements";
string :references = "Project website at http://www.earlinet.org";
string :__file_format_version = "2.0";
string :Conventions = "CF-1.7";
:hoi_system_ID = 74;
:hoi_configuration_ID = 124;
string :input_file = "20120710po00_0000291.nc";
string :measurement_start_datetime = "2012-07-09T22:59:39Z";
string :measurement_stop_datetime = "2012-07-09T23:59:26Z";
```

## e532

```text
dimensions:
    altitude = 245;
    time = 1;
    wavelength = 1;
    nv = 2;

variables:
    double altitude(altitude);
        string altitude:long_name = "height above sea level";
        string altitude:units = "m";
        string altitude:axis = "Z";
        string altitude:positive = "up";
        string altitude:standard_name = "altitude";

    double time(time);
        string time:long_name = "time";
        string time:units = "seconds since 1970-01-01T00:00:00Z";
        string time:axis = "T";
        string time:standard_name = "time";
        string time:bounds = "time_bounds";
        string time:calendar = "gregorian";

    double time_bounds(time, nv);

    double vertical_resolution(wavelength, time, altitude);
        vertical_resolution:_FillValue = 9.969209968386869E36;
        string vertical_resolution:long_name = "effective vertical resolution according to Pappalardo et al., appl. opt. 2004";
        string vertical_resolution:units = "m";

    byte cloud_mask(time, altitude);
        cloud_mask:_FillValue = -127B;
        string cloud_mask:long_name = "cloud mask";
        string cloud_mask:units = "1";
        cloud_mask:flag_masks = 1B, 2B, 4B;
        string cloud_mask:flag_meanings = "unknown_cloud cirrus_cloud water_cloud";
        cloud_mask:valid_range = 0B, 7B;

    byte cirrus_contamination;
        cirrus_contamination:_FillValue = -127B;
        string cirrus_contamination:long_name = "do the profiles contain cirrus layers?";
        cirrus_contamination:flag_values = 0B, 1B, 2B;
        string cirrus_contamination:flag_meanings = "not_available no_cirrus cirrus_detected";

    byte error_retrieval_method(wavelength);
        error_retrieval_method:_FillValue = -127B;
        string error_retrieval_method:long_name = "method used for the retrieval of uncertainties";
        error_retrieval_method:flag_values = 0B, 1B;
        string error_retrieval_method:flag_meanings = "monte_carlo error_propagation";

    byte extinction_evaluation_algorithm(wavelength);
        extinction_evaluation_algorithm:_FillValue = -127B;
        string extinction_evaluation_algorithm:long_name = "algorithm used for the extinction retrieval";
        extinction_evaluation_algorithm:flag_values = 0B, 1B;
        string extinction_evaluation_algorithm:flag_meanings = "weighted_linear_fit non-weighted_linear_fit";

    double extinction(wavelength, time, altitude);
        extinction:_FillValue = 9.969209968386869E36;
        string extinction:long_name = "aerosol extinction coefficient";
        string extinction:ancillary_variables = "error_extinction vertical_resolution";
        string extinction:coordinates = "longitude latitude";
        string extinction:units = "1/m";

    double error_extinction(wavelength, time, altitude);
        error_extinction:_FillValue = 9.969209968386869E36;
        string error_extinction:long_name = "absolute statistical uncertainty of extinction";
        string error_extinction:units = "1/m";
        string error_extinction:coordinates = "longitude latitude";

    int user_defined_category;
        user_defined_category:_FillValue = -2147483647;
        string user_defined_category:long_name = "user defined category of the measurement";
        string user_defined_category:comment = "Those flags might have not been set in a homogeneous way. Before using them, contact the originator to obtain more detailed information on how these flags have been set.";
        user_defined_category:flag_masks = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512;
        string user_defined_category:flag_meanings = "cirrus climatol dicycles etna forfires photosmog rurban sahadust stratos satellite_overpasses";
        user_defined_category:valid_range = 0, 1023;

    byte cirrus_contamination_source;
        cirrus_contamination_source:_FillValue = -127B;
        string cirrus_contamination_source:long_name = "how was cirrus_contamination obtained?";
        cirrus_contamination_source:flag_values = 0B, 1B, 2B;
        string cirrus_contamination_source:flag_meanings = "not_available user_provided automatic_calculated";

    byte atmospheric_molecular_calculation_source;
        atmospheric_molecular_calculation_source:_FillValue = -127B;
        string atmospheric_molecular_calculation_source:long_name = "data source of the atmospheric molecular calculations";
        atmospheric_molecular_calculation_source:flag_values = 0B, 1B, 2B, 3B, 4B;
        string atmospheric_molecular_calculation_source:flag_meanings = "US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas";

    float latitude;
        string latitude:standard_name = "latitude";
        string latitude:long_name = "latitude of station";
        string latitude:units = "degrees_north";

    float longitude;
        string longitude:long_name = "longitude of station";
        string longitude:units = "degrees_east";
        string longitude:standard_name = "longitude";

    float station_altitude;
        station_altitude:_FillValue = 9.96921E36f;
        string station_altitude:long_name = "station altitude above sea level";
        string station_altitude:units = "m";

    float extinction_assumed_wavelength_dependence(wavelength);
        extinction_assumed_wavelength_dependence:_FillValue = 9.96921E36f;
        string extinction_assumed_wavelength_dependence:long_name = "assumed wavelength dependence for extinction retrieval";
        string extinction_assumed_wavelength_dependence:units = "1";

    float wavelength(wavelength);
        string wavelength:long_name = "wavelength of the transmitted laser pulse";
        string wavelength:units = "nm";

    float zenith_angle;
        zenith_angle:_FillValue = 9.96921E36f;
        string zenith_angle:long_name = "laser pointing angle with respect to the zenith";
        string zenith_angle:units = "degrees";

    int shots;
        shots:_FillValue = -2147483647;
        string shots:long_name = "accumulated laser shots";
        string shots:units = "1";

    int earlinet_product_type;
        earlinet_product_type:_FillValue = -2147483647;
        string earlinet_product_type:long_name = "Earlinet product type";
        earlinet_product_type:flag_values = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14;
        string earlinet_product_type:flag_meanings = "e0355 b0355 e0351 b0351 e0532 b0532 e1064 b1064 b0253 b0313 b0335 b0510 b0694 b0817";
        earlinet_product_type:valid_range = 1, 14;

    double backscatter(wavelength, time, altitude);
        backscatter:_FillValue = 9.969209968386869E36;
        string backscatter:long_name = "aerosol backscatter coefficient";
        string backscatter:units = "1/(m*sr)";
        string backscatter:ancillary_variables = "error_backscatter vertical_resolution";
        string backscatter:coordinates = "longitude latitude";

    double error_backscatter(wavelength, time, altitude);
        error_backscatter:_FillValue = 9.969209968386869E36;
        string error_backscatter:long_name = "absolute statistical uncertainty of backscatter";
        string error_backscatter:units = "1/(m*sr)";
        string error_backscatter:coordinates = "longitude latitude";

    byte backscatter_calibration_range_search_algorithm(wavelength);
        backscatter_calibration_range_search_algorithm:_FillValue = -127B;
        string backscatter_calibration_range_search_algorithm:long_name = "algorithm used for the search of the calibration_range";
        backscatter_calibration_range_search_algorithm:flag_values = 0B, 1B;
        string backscatter_calibration_range_search_algorithm:flag_meanings = "minimum_of_signal_ratio minimum_of_elastic_signal";

    float backscatter_calibration_range(wavelength, nv);
        backscatter_calibration_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_range:long_name = "height range where calibration was calculated";
        string backscatter_calibration_range:units = "m";

    byte backscatter_evaluation_method(wavelength);
        backscatter_evaluation_method:_FillValue = -127B;
        string backscatter_evaluation_method:long_name = "method used for the backscatter retrieval";
        backscatter_evaluation_method:flag_values = 0B, 1B;
        string backscatter_evaluation_method:flag_meanings = "Raman elastic_backscatter";

    byte raman_backscatter_algorithm(wavelength);
        raman_backscatter_algorithm:_FillValue = -127B;
        string raman_backscatter_algorithm:long_name = "algorithm used for the retrieval of the Raman backscatter profile";
        raman_backscatter_algorithm:flag_values = 0B, 1B;
        string raman_backscatter_algorithm:flag_meanings = "Ansmann via_backscatter_ratio";

    float backscatter_calibration_value(wavelength);
        backscatter_calibration_value:_FillValue = 9.96921E36f;
        string backscatter_calibration_value:long_name = "assumed backscatter-ratio value (unitless) in calibration range";
        string backscatter_calibration_value:units = "1";

    float backscatter_calibration_search_range(wavelength, nv);
        backscatter_calibration_search_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_search_range:long_name = "height range wherein calibration range is searched";
        string backscatter_calibration_search_range:units = "m";

// global attributes:
string :measurement_ID = "20120710po00";
string :system = "MUSA";
string :institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA), Potenza - CNR-IMAA";
string :location = "Potenza, Italy";
string :station_ID = "pot";
string :PI = "Aldo Amodeo";
string :PI_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale ";
string :PI_affiliation_acronym = "CNR-IMAA";
string :PI_address = "Contrada S.Loja, Zona Industriale - Tito Scalo I-85050 Potenza";
string :PI_phone = "+39 0971 427263";
string :PI_email = "aldo.amodeo@imaa.cnr.it";
string :Data_Originator = "damico";
string :Data_Originator_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale";
string :Data_Originator_affiliation_acronym = "CNR-IMAA";
string :Data_Originator_address = "C.da S. Loja - Zona Industriale, 85050 Potenza, Italy";
string :Data_Originator_phone = "+39 0971 427297";
string :Data_Originator_email = "giuseppe.damico@imaa.cnr.it";
string :data_processing_institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA)";
string :comment = "charmex pre-campaign";
string :scc_version = "5.1.0";
string :scc_version_description = "SCC vers. 5.1.0 (HiRELPP vers. 1.0.6, CloudMask vers. 1.1.8, ELPP vers. 7.0.5, ELDA vers. 3.3.9, ELIC vers. 1.0.3, ELQUICK vers. 1.0.3, ELDEC vers. 2.0.1)";
string :processor_name = "ELDA";
string :processor_version = "3.3.9";
string :history = "2019-06-05T17:32:14Z: elpp -d sccoperational -m 20120710po00 -c elpp.config; 2019-06-05T18:47:26Z: elda 20120710po00 -c elda.ini";
string :title = "Profiles of aerosol optical properties";
string :source = "Ground based LIDAR measurements";
string :references = "Project website at http://www.earlinet.org";
string :__file_format_version = "2.0";
string :Conventions = "CF-1.7";
:hoi_system_ID = 74;
:hoi_configuration_ID = 124;
string :input_file = "20120710po00_0000471.nc";
string :measurement_start_datetime = "2012-07-09T22:59:39Z";
string :measurement_stop_datetime = "2012-07-09T23:59:26Z";
```

## b532

```text
dimensions:
    altitude = 245;
    time = 1;
    wavelength = 1;
    nv = 2;

    variables:
    double altitude(altitude);
        string altitude:long_name = "height above sea level";
        string altitude:units = "m";
        string altitude:axis = "Z";
        string altitude:positive = "up";
        string altitude:standard_name = "altitude";

    double time(time);
        string time:long_name = "time";
        string time:units = "seconds since 1970-01-01T00:00:00Z";
        string time:axis = "T";
        string time:standard_name = "time";
        string time:bounds = "time_bounds";
        string time:calendar = "gregorian";

    double time_bounds(time, nv);

    double vertical_resolution(wavelength, time, altitude);
        vertical_resolution:_FillValue = 9.969209968386869E36;
        string vertical_resolution:long_name = "effective vertical resolution according to Pappalardo et al., appl. opt. 2004";
        string vertical_resolution:units = "m";

    byte cloud_mask(time, altitude);
        cloud_mask:_FillValue = -127B;
        string cloud_mask:long_name = "cloud mask";
        string cloud_mask:units = "1";
        cloud_mask:flag_masks = 1B, 2B, 4B;
        string cloud_mask:flag_meanings = "unknown_cloud cirrus_cloud water_cloud";
        cloud_mask:valid_range = 0B, 7B;

    byte cirrus_contamination;
        cirrus_contamination:_FillValue = -127B;
        string cirrus_contamination:long_name = "do the profiles contain cirrus layers?";
        cirrus_contamination:flag_values = 0B, 1B, 2B;
        string cirrus_contamination:flag_meanings = "not_available no_cirrus cirrus_detected";

    byte error_retrieval_method(wavelength);
        error_retrieval_method:_FillValue = -127B;
        string error_retrieval_method:long_name = "method used for the retrieval of uncertainties";
        error_retrieval_method:flag_values = 0B, 1B;
        string error_retrieval_method:flag_meanings = "monte_carlo error_propagation";

    byte backscatter_evaluation_method(wavelength);
        backscatter_evaluation_method:_FillValue = -127B;
        string backscatter_evaluation_method:long_name = "method used for the backscatter retrieval";
        backscatter_evaluation_method:flag_values = 0B, 1B;
        string backscatter_evaluation_method:flag_meanings = "Raman elastic_backscatter";

    byte raman_backscatter_algorithm(wavelength);
        raman_backscatter_algorithm:_FillValue = -127B;
        string raman_backscatter_algorithm:long_name = "algorithm used for the retrieval of the Raman backscatter profile";
        raman_backscatter_algorithm:flag_values = 0B, 1B;
        string raman_backscatter_algorithm:flag_meanings = "Ansmann via_backscatter_ratio";

    double backscatter(wavelength, time, altitude);
        backscatter:_FillValue = 9.969209968386869E36;
        string backscatter:long_name = "aerosol backscatter coefficient";
        string backscatter:units = "1/(m*sr)";
        string backscatter:ancillary_variables = "error_backscatter vertical_resolution";
        string backscatter:coordinates = "longitude latitude";

    double error_backscatter(wavelength, time, altitude);
        error_backscatter:_FillValue = 9.969209968386869E36;
        string error_backscatter:long_name = "absolute statistical uncertainty of backscatter";
        string error_backscatter:units = "1/(m*sr)";
        string error_backscatter:coordinates = "longitude latitude";

    int user_defined_category;
        user_defined_category:_FillValue = -2147483647;
        string user_defined_category:long_name = "user defined category of the measurement";
        string user_defined_category:comment = "Those flags might have not been set in a homogeneous way. Before using them, contact the originator to obtain more detailed information on how these flags have been set.";
        user_defined_category:flag_masks = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512;
        string user_defined_category:flag_meanings = "cirrus climatol dicycles etna forfires photosmog rurban sahadust stratos satellite_overpasses";
        user_defined_category:valid_range = 0, 1023;

    byte cirrus_contamination_source;
        cirrus_contamination_source:_FillValue = -127B;
        string cirrus_contamination_source:long_name = "how was cirrus_contamination obtained?";
        cirrus_contamination_source:flag_values = 0B, 1B, 2B;
        string cirrus_contamination_source:flag_meanings = "not_available user_provided automatic_calculated";

    byte atmospheric_molecular_calculation_source;
        atmospheric_molecular_calculation_source:_FillValue = -127B;
        string atmospheric_molecular_calculation_source:long_name = "data source of the atmospheric molecular calculations";
        atmospheric_molecular_calculation_source:flag_values = 0B, 1B, 2B, 3B, 4B;
        string atmospheric_molecular_calculation_source:flag_meanings = "US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas";

    float latitude;
        string latitude:long_name = "latitude of station";
        string latitude:units = "degrees_north";
        string latitude:standard_name = "latitude";

    float longitude;
        string longitude:long_name = "longitude of station";
        string longitude:units = "degrees_east";
        string longitude:standard_name = "longitude";

    float station_altitude;
        station_altitude:_FillValue = 9.96921E36f;
        string station_altitude:long_name = "station altitude above sea level";
        string station_altitude:units = "m";

    float backscatter_calibration_value(wavelength);
        backscatter_calibration_value:_FillValue = 9.96921E36f;
        string backscatter_calibration_value:long_name = "assumed backscatter-ratio value (unitless) in calibration range";
        string backscatter_calibration_value:units = "1";

    float backscatter_calibration_search_range(wavelength, nv);
        backscatter_calibration_search_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_search_range:long_name = "height range wherein calibration range is searched";
        string backscatter_calibration_search_range:units = "m";

    float wavelength(wavelength);
        string wavelength:long_name = "wavelength of the transmitted laser pulse";
        string wavelength:units = "nm";

    float zenith_angle;
        zenith_angle:_FillValue = 9.96921E36f;
        string zenith_angle:long_name = "laser pointing angle with respect to the zenith";
        string zenith_angle:units = "degrees";

    int shots;
        shots:_FillValue = -2147483647;
        string shots:long_name = "accumulated laser shots";
        string shots:units = "1";

    int earlinet_product_type;
        earlinet_product_type:_FillValue = -2147483647;
        string earlinet_product_type:long_name = "Earlinet product type";
        earlinet_product_type:flag_values = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14;
        string earlinet_product_type:flag_meanings = "e0355 b0355 e0351 b0351 e0532 b0532 e1064 b1064 b0253 b0313 b0335 b0510 b0694 b0817";
        earlinet_product_type:valid_range = 1, 14;

    byte backscatter_calibration_range_search_algorithm(wavelength);
        backscatter_calibration_range_search_algorithm:_FillValue = -127B;
        string backscatter_calibration_range_search_algorithm:long_name = "algorithm used for the search of the calibration_range";
        backscatter_calibration_range_search_algorithm:flag_values = 0B, 1B;
        string backscatter_calibration_range_search_algorithm:flag_meanings = "minimum_of_signal_ratio minimum_of_elastic_signal";

    float backscatter_calibration_range(wavelength, nv);
        string backscatter_calibration_range:long_name = "height range where calibration was calculated";
        string backscatter_calibration_range:units = "m";
        backscatter_calibration_range:_FillValue = 9.96921E36f;

    double volumedepolarization(wavelength, time, altitude);
        volumedepolarization:_FillValue = 9.969209968386869E36;
        string volumedepolarization:long_name = "volume linear depolarization ratio";
        string volumedepolarization:units = "1";
        string volumedepolarization:ancillary_variables = "error_volumedepolarization vertical_resolution";
        string volumedepolarization:coordinates = "longitude latitude";

    double error_volumedepolarization(wavelength, time, altitude);
        error_volumedepolarization:_FillValue = 9.969209968386869E36;
        string error_volumedepolarization:long_name = "absolute statistical uncertainty of volumedepolarization";
        string error_volumedepolarization:units = "1";
        string error_volumedepolarization:coordinates = "longitude latitude";

    double particledepolarization(wavelength, time, altitude);
        particledepolarization:_FillValue = 9.969209968386869E36;
        string particledepolarization:long_name = "particle linear depolarization ratio";
        string particledepolarization:units = "1";
        string particledepolarization:ancillary_variables = "error_particledepolarization vertical_resolution";
        string particledepolarization:coordinates = "longitude latitude";

    double error_particledepolarization(wavelength, time, altitude);
        error_particledepolarization:_FillValue = 9.969209968386869E36;
        string error_particledepolarization:long_name = "absolute statistical uncertainty of particledepolarization";
        string error_particledepolarization:units = "1";
        string error_particledepolarization:coordinates = "longitude latitude";

// global attributes:
string :measurement_ID = "20120710po00";
string :system = "MUSA";
string :institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA), Potenza - CNR-IMAA";
string :location = "Potenza, Italy";
string :station_ID = "pot";
string :PI = "Aldo Amodeo";
string :PI_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale ";
string :PI_affiliation_acronym = "CNR-IMAA";
string :PI_address = "Contrada S.Loja, Zona Industriale - Tito Scalo I-85050 Potenza";
string :PI_phone = "+39 0971 427263";
string :PI_email = "aldo.amodeo@imaa.cnr.it";
string :Data_Originator = "damico";
string :Data_Originator_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale";
string :Data_Originator_affiliation_acronym = "CNR-IMAA";
string :Data_Originator_address = "C.da S. Loja - Zona Industriale, 85050 Potenza, Italy";
string :Data_Originator_phone = "+39 0971 427297";
string :Data_Originator_email = "giuseppe.damico@imaa.cnr.it";
string :data_processing_institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA)";
string :comment = "charmex pre-campaign";
string :scc_version = "5.1.0";
string :scc_version_description = "SCC vers. 5.1.0 (HiRELPP vers. 1.0.6, CloudMask vers. 1.1.8, ELPP vers. 7.0.5, ELDA vers. 3.3.9, ELIC vers. 1.0.3, ELQUICK vers. 1.0.3, ELDEC vers. 2.0.1)";
string :processor_name = "ELDA";
string :processor_version = "3.3.9";
string :history = "2019-06-05T17:32:17Z: elpp -d sccoperational -m 20120710po00 -c elpp.config; 2019-06-05T18:47:27Z: elda 20120710po00 -c elda.ini";
string :title = "Profiles of aerosol optical properties";
string :source = "Ground based LIDAR measurements";
string :references = "Project website at http://www.earlinet.org";
string :__file_format_version = "2.0";
string :Conventions = "CF-1.7";
:hoi_system_ID = 74;
:hoi_configuration_ID = 124;
string :input_file = "20120710po00_0000691.nc";
string :measurement_start_datetime = "2012-07-09T22:59:39Z";
string :measurement_stop_datetime = "2012-07-09T23:59:26Z";
```

## b1064

```text
dimensions:
    altitude = 245;
    time = 1;
    wavelength = 1;
    nv = 2;

variables:
    double altitude(altitude);
        string altitude:long_name = "height above sea level";
        string altitude:units = "m";
        string altitude:axis = "Z";
        string altitude:positive = "up";
        string altitude:standard_name = "altitude";

    double time(time);
        string time:long_name = "time";
        string time:units = "seconds since 1970-01-01T00:00:00Z";
        string time:axis = "T";
        string time:standard_name = "time";
        string time:bounds = "time_bounds";
        string time:calendar = "gregorian";

    double time_bounds(time, nv);

    double vertical_resolution(wavelength, time, altitude);
        vertical_resolution:_FillValue = 9.969209968386869E36;
        string vertical_resolution:long_name = "effective vertical resolution according to Pappalardo et al., appl. opt. 2004";
        string vertical_resolution:units = "m";

    byte cloud_mask(time, altitude);
        cloud_mask:_FillValue = -127B;
        string cloud_mask:long_name = "cloud mask";
        string cloud_mask:units = "1";
        cloud_mask:flag_masks = 1B, 2B, 4B;
        string cloud_mask:flag_meanings = "unknown_cloud cirrus_cloud water_cloud";
        cloud_mask:valid_range = 0B, 7B;

    byte cirrus_contamination;
        cirrus_contamination:_FillValue = -127B;
        string cirrus_contamination:long_name = "do the profiles contain cirrus layers?";
        cirrus_contamination:flag_values = 0B, 1B, 2B;
        string cirrus_contamination:flag_meanings = "not_available no_cirrus cirrus_detected";

    byte error_retrieval_method(wavelength);
        error_retrieval_method:_FillValue = -127B;
        string error_retrieval_method:long_name = "method used for the retrieval of uncertainties";
        error_retrieval_method:flag_values = 0B, 1B;
        string error_retrieval_method:flag_meanings = "monte_carlo error_propagation";

    byte backscatter_evaluation_method(wavelength);
        backscatter_evaluation_method:_FillValue = -127B;
        string backscatter_evaluation_method:long_name = "method used for the backscatter retrieval";
        backscatter_evaluation_method:flag_values = 0B, 1B;
        string backscatter_evaluation_method:flag_meanings = "Raman elastic_backscatter";

    byte elastic_backscatter_algorithm(wavelength);
        elastic_backscatter_algorithm:_FillValue = -127B;
        string elastic_backscatter_algorithm:long_name = "algorithm used for the retrieval of the backscatter profile";
        elastic_backscatter_algorithm:flag_values = 0B, 1B;
        string elastic_backscatter_algorithm:flag_meanings = "Klett-Fernald iterative";

    double backscatter(wavelength, time, altitude);
        backscatter:_FillValue = 9.969209968386869E36;
        string backscatter:long_name = "aerosol backscatter coefficient";
        string backscatter:units = "1/(m*sr)";
        string backscatter:ancillary_variables = "error_backscatter vertical_resolution";
        string backscatter:coordinates = "longitude latitude";

    double error_backscatter(wavelength, time, altitude);
        error_backscatter:_FillValue = 9.969209968386869E36;
        string error_backscatter:long_name = "absolute statistical uncertainty of backscatter";
        string error_backscatter:units = "1/(m*sr)";
        string error_backscatter:coordinates = "longitude latitude";

    int user_defined_category;
        user_defined_category:_FillValue = -2147483647;
        string user_defined_category:long_name = "user defined category of the measurement";
        string user_defined_category:comment = "Those flags might have not been set in a homogeneous way. Before using them, contact the originator to obtain more detailed information on how these flags have been set.";
        user_defined_category:flag_masks = 1, 2, 4, 8, 16, 32, 64, 128, 256, 512;
        string user_defined_category:flag_meanings = "cirrus climatol dicycles etna forfires photosmog rurban sahadust stratos satellite_overpasses";
        user_defined_category:valid_range = 0, 1023;

    byte cirrus_contamination_source;
        cirrus_contamination_source:_FillValue = -127B;
        string cirrus_contamination_source:long_name = "how was cirrus_contamination obtained?";
        cirrus_contamination_source:flag_values = 0B, 1B, 2B;
        string cirrus_contamination_source:flag_meanings = "not_available user_provided automatic_calculated";

    byte atmospheric_molecular_calculation_source;
        atmospheric_molecular_calculation_source:_FillValue = -127B;
        string atmospheric_molecular_calculation_source:long_name = "data source of the atmospheric molecular calculations";
        atmospheric_molecular_calculation_source:flag_values = 0B, 1B, 2B, 3B, 4B;
        string atmospheric_molecular_calculation_source:flag_meanings = "US_standard_atmosphere radiosounding ecmwf icon-iglo-12-23 gdas";

    float latitude;
        string latitude:long_name = "latitude of station";
        string latitude:units = "degrees_north";
        string latitude:standard_name = "latitude";

    float longitude;
        string longitude:long_name = "longitude of station";
        string longitude:units = "degrees_east";
        string longitude:standard_name = "longitude";

    float station_altitude;
        station_altitude:_FillValue = 9.96921E36f;
        string station_altitude:long_name = "station altitude above sea level";
        string station_altitude:units = "m";

    float backscatter_calibration_value(wavelength);
        backscatter_calibration_value:_FillValue = 9.96921E36f;
        string backscatter_calibration_value:long_name = "assumed backscatter-ratio value (unitless) in calibration range";
        string backscatter_calibration_value:units = "1";

    float backscatter_calibration_search_range(wavelength, nv);
        backscatter_calibration_search_range:_FillValue = 9.96921E36f;
        string backscatter_calibration_search_range:long_name = "height range wherein calibration range is searched";
        string backscatter_calibration_search_range:units = "m";

    float wavelength(wavelength);
        string wavelength:long_name = "wavelength of the transmitted laser pulse";
        string wavelength:units = "nm";

    float zenith_angle;
        zenith_angle:_FillValue = 9.96921E36f;
        string zenith_angle:long_name = "laser pointing angle with respect to the zenith";
        string zenith_angle:units = "degrees";

    int shots;
        shots:_FillValue = -2147483647;
        string shots:long_name = "accumulated laser shots";
        string shots:units = "1";

    int earlinet_product_type;
        earlinet_product_type:_FillValue = -2147483647;
        string earlinet_product_type:long_name = "Earlinet product type";
        earlinet_product_type:flag_values = 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14;
        string earlinet_product_type:flag_meanings = "e0355 b0355 e0351 b0351 e0532 b0532 e1064 b1064 b0253 b0313 b0335 b0510 b0694 b0817";
        earlinet_product_type:valid_range = 1, 14;

    byte backscatter_calibration_range_search_algorithm(wavelength);
        backscatter_calibration_range_search_algorithm:_FillValue = -127B;
        string backscatter_calibration_range_search_algorithm:long_name = "algorithm used for the search of the calibration_range";
        backscatter_calibration_range_search_algorithm:flag_values = 0B, 1B;
        string backscatter_calibration_range_search_algorithm:flag_meanings = "minimum_of_signal_ratio minimum_of_elastic_signal";

    float backscatter_calibration_range(wavelength, nv);
        string backscatter_calibration_range:long_name = "height range where calibration was calculated";
        string backscatter_calibration_range:units = "m";
        backscatter_calibration_range:_FillValue = 9.96921E36f;

// global attributes:
string :measurement_ID = "20120710po00";
string :system = "MUSA";
string :institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA), Potenza - CNR-IMAA";
string :location = "Potenza, Italy";
string :station_ID = "pot";
string :PI = "Aldo Amodeo";
string :PI_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale ";
string :PI_affiliation_acronym = "CNR-IMAA";
string :PI_address = "Contrada S.Loja, Zona Industriale - Tito Scalo I-85050 Potenza";
string :PI_phone = "+39 0971 427263";
string :PI_email = "aldo.amodeo@imaa.cnr.it";
string :Data_Originator = "damico";
string :Data_Originator_affiliation = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale";
string :Data_Originator_affiliation_acronym = "CNR-IMAA";
string :Data_Originator_address = "C.da S. Loja - Zona Industriale, 85050 Potenza, Italy";
string :Data_Originator_phone = "+39 0971 427297";
string :Data_Originator_email = "giuseppe.damico@imaa.cnr.it";
string :data_processing_institution = "Consiglio Nazionale delle Ricerche - Istituto di Metodologie per l\'Analisi Ambientale (CNR-IMAA)";
string :comment = "charmex pre-campaign";
string :scc_version = "5.1.0";
string :scc_version_description = "SCC vers. 5.1.0 (HiRELPP vers. 1.0.6, CloudMask vers. 1.1.8, ELPP vers. 7.0.5, ELDA vers. 3.3.9, ELIC vers. 1.0.3, ELQUICK vers. 1.0.3, ELDEC vers. 2.0.1)";
string :processor_name = "ELDA";
string :processor_version = "3.3.9";
string :history = "2019-06-05T17:32:09Z: elpp -d sccoperational -m 20120710po00 -c elpp.config; 2019-06-05T18:47:27Z: elda 20120710po00 -c elda.ini";
string :title = "Profiles of aerosol optical properties";
string :source = "Ground based LIDAR measurements";
string :references = "Project website at http://www.earlinet.org";
string :__file_format_version = "2.0";
string :Conventions = "CF-1.7";
:hoi_system_ID = 74;
:hoi_configuration_ID = 124;
string :input_file = "20120710po00_0000293.nc";
string :measurement_start_datetime = "2012-07-09T22:59:39Z";
string :measurement_stop_datetime = "2012-07-09T23:59:26Z";
```