# TODO list for new pipelines

1. Edit `openfido.py` to implement your pipeline python3 code.

2. Add modules used to `requirements.txt`.

3. Create autotests in folders names `autotest/input_{1,2,...}`. Always create a `config.csv` and add any supporting data files required for the validation test.

4. Commit and publish you new pipeline to GitHub.

5. Edit `README.md` to document your pipeline's functionality. Delete everthing above the validation badge (below the horizontal line) when you are done.

----

[![validation](https://github.com/openfido/PIPELINE_NAME/actions/workflows/main.yml/badge.svg)](https://github.com/openfido/PIPELINE_NAME/actions/workflows/main.yml)

*Insert a one-line description of the pipeline's function here.*

*You may add additional details here about the pipelines function here.*

CONFIG
------

The following parameters are recognized in `config.csv`:

* `PARAMETER_1`: *Add an entry for each parameter here. Indicate whether the parameter is required and provide an example and/or explanation of the parameter value's format.  If optional, indicate what the default value is.*

* `PARAMETER_2`: *Add additional parameters here.*

INPUT
-----

The following files are accepted as input folder.

* `INPUT_1`: *Add an entry for each input file here.  Provide information regarding the valid file formats and how they are affected by entries in `config.csv`.*

* `INPUT_2`: *Add additional input file information here.*

OUTPUT
------

The following files are generated in the output folder.

* `OUTPUT_1`: *Add an entry for each output file here.  Provide information regarding the valid file formats and how they are affected by entries in `config.csv`.*

* `OUTPUT_2`: *Add additional output file information here.*
