[![validation](https://github.com/openfido/census/actions/workflows/main.yml/badge.svg)](https://github.com/openfido/census/actions/workflows/main.yml)

Census TIGER geographic data retrieval.

CONFIG
------

The following parameters are recognized in `config.csv`:

* `INPUT_FILENAME`: Specifies the input filename. Optional, default is `input.csv`.

* `OUTPUT_FILENAME`: Specifies the output filename. Optional, default is `output.csv`.

* `STATE_FIELDS`: Specifies the state fields to retrieve. Valid fields are `REGION`, `DIVISION`, `STATEFP`, `STATENS`, `GEOID`, `STUSPS`, `NAME`, `LSAD`, `MTFCC`, `FUNCSTAT`, `ALAND`, `AWATER`, `INTPTLAT`, `INTPTLON`, `geometry`. Optional, default is `*`.  

* `ZIPCODE_FIELDS`: Specifies the zipcode fields to retrieve. `ZCTA5CE10`, `GEOID10`, `CLASSFP10`, `MTFCC10`, `FUNCSTAT10`, `ALAND10`, `AWATER10`, `INTPTLAT10`, `INTPTLON10`, `geometry`. Optional, default is `*`.

INPUT
-----

The following files are accepted as input folder.

* `input.csv`: The input file must provide the `latitude` and `longitude` fields.

OUTPUT
------

The following files are generated in the output folder.

* `output.csv`: The output file will include the requested state and zipcode fields, as well as all the input fields.
