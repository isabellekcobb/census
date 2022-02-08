"""PIPELINE_NAME pipeline for OpenFIDO

TODO: copy the contents of the README.md file here.

"""

version = 1 # specify API version for this pipeline

NAME = "PIPELINE_NAME" # TODO: set this to your pipeline name
DEBUG = False
OPENFIDO_INPUT = os.getenv("OPENFIDO_INPUT")
OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

try:

    if not OPENFIDO_INPUT:
        raise RuntimeError("OPENFIDO_INPUT not defined in the environment")

    if not OPENFIDO_INPUT:
        raise RuntimeError("OPENFIDO_OUTPUT not defined in the environment")

    # TODO: process the input files and generate the output files

    exit(0) # success

except Exception as err:

    if DEBUG:
        raise
    print(f"ERROR [{NAME}]: {err}",file=sys.stderr)
    exit(1)
