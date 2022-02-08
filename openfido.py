"""Address resolution pipeline

The address resolution pipeline resolves addresses and locations.

CONFIG
------

The following parameters are recognized in `config.csv`:

* DATA: The CSV data file name contain address or location (required)

* REVERSE: Boolean value indicating whether the data contains locations
  (False, default) or addresses (True)

* PROVIDER: Resolver provider (default is "nominatim")

* USER_AGENT: Resolver user agent (default is "csv_user_ht")

* TIMEOUT: Resolver timeout in seconds (default is 5)

* RETRIES: Resolver retry limit (default is 5)

* SLEEP: Resolver sleep between retries in seconds (default 1)

INPUT
-----

The format of the input depends on the value of REVERSE in config.csv.

* REVERSE=False

The CSV file must include a *latitude* and *longitude* column.

* REVERSE=True

The CSV file must include an *address* column.

OUTPUT
------

The format of the output depends on the value of REVERSE in config.csv.

* REVERSE=False

The CSV file will include an *address* column.

* REVERSE=True

The CSV file will include a *latitude* and *longitude* column.

"""

version = 1 # specify API version

import sys, os
import json, csv
import pandas as pd
from shapely.geometry import Point
from geopandas.tools import geocode, reverse_geocode

NAME = "census" 
OPENFIDO_INPUT = os.getenv("OPENFIDO_INPUT")
OPENFIDO_OUTPUT = os.getenv("OPENFIDO_OUTPUT")

#
# Defaults
#
OPTIONS = {
    "state_fields" : "STUSPS",
    "zipcode_fields" : "ZCTA5CE10",
    "tract_fields" : "",}

CONFIG = {
    "verbose" : False,
    "debug" : False,
    "warning" : True,
    "quiet" : False,
    "urladdr" : "https://www2.census.gov/geo/tiger/TIGER2020",
    "cachedir" : "/usr/local/share/gridlabd/geodata/census",
    "states_filename" : "tl_2020_us_state.zip",
    "zipcode_filename" : "tl_2020_us_zcta510.zip",

    # See https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2020&layergroup=Census+Tracts
    "tract_filename" : "TRACT/tl_2020_<state_tract_code>_tract.zip",

    # See https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf
    "single_address_resolution" : "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress?address=<address>&benchmark=2020&vintage=2010&format=json",

    # CSV upload must contain the following fields: "Unique ID, Street address, City, State, ZIP"
    "batch_address_resolution" : "https://geocoding.geo.census.gov/geocoder/returntype/addressbatch",
}

#
# Utilities
#
class MissingEnvironment(Exception):
    """Raised when required environment variables are not defined properly"""
    pass

class MissingInput(Exception):
    pass

def verbose(msg):
    if CONFIG["verbose"]:
        print(f"VERBOSE [{NAME}]: {msg}", file=sys.stderr)

def error(msg,exception=None):
    if not CONFIG["quiet"]:
        print(f"ERROR [{NAME}]: {msg}", file=sys.stderr)
    if exception:
        raise exception(msg)
    elif CONFIG["debug"]:
        import traceback
        for line in tracekback.format_stack():
            print(line.strip(),file=sys.stderr)

def debug(msg):
    if CONFIG["debug"]:
        print(f"DEBUG [{NAME}]: {msg}", file=sys.stderr)

def warning(msg):
    if CONFIG["warning"]:
        print(f"WARNING [{NAME}]: {msg}", file=sys.stderr)

def load_config():
    
    global OPENFIDO_INPUT
    if not OPENFIDO_INPUT:
        raise MissingEnvironment("OPENFIDO_INPUT not defined in the environment")
    if not OPENFIDO_INPUT.endswith("/"):
        OPENFIDO_INPUT += "/"

    global OPENFIDO_OUTPUT
    if not OPENFIDO_OUTPUT:
        raise MissingEnvironment("OPENFIDO_OUTPUT not defined in the environment")    
    if not OPENFIDO_OUTPUT.endswith("/"):
        OPENFIDO_OUTPUT += "/"

    with open(f"{OPENFIDO_INPUT}/config.csv","r") as cfg:
        reader = csv.reader(cfg)
        def cast(x,astype):
            if astype is bool:
                try:
                    return int(x)
                except:
                    if x.lower() in ("yes","true","no","false"):
                        return x.lower() in ("yes","true")
                    error(f"'{x}' is not a valid boolean value",Exception)
            else:
                return astype(x)
        for row in reader:
            row0 = row[0].lower()
            if row0 == "data":
                DATA = pd.read_csv(f"{OPENFIDO_INPUT}/{row[1]}")
            elif row0 in CONFIG.keys():
                if len(row) == 1:
                    CONFIG[row0] = True
                else:
                    CONFIG[row0] = cast(row[1],type(CONFIG[row0]))
            elif row0 in OPTIONS.keys():
                if len(row) == 1:
                    OPTIONS[row0] = True
                else:   
                    OPTIONS[row0] = cast(row[1],type(CONFIG[row0]))
            else:
                error(f"config.csv parameter {row[0]} is not valid",Exception)

#
# Implementation of address package
#
state_tract_codes = {
    '01':'AL',
    '02':'AK',
    '04':'AZ',
    '05':'AR',
    '06':'CA',
    '08':'CO',
    '09':'CT',
    '10':'DE',
    '11':'DC',
    '12':'FL',
    '13':'GA',
    '15':'HI',
    '16':'ID',
    '17':'IL',
    '18':'IN',
    '19':'IA',
    '20':'KS',
    '21':'KY',
    '22':'LA',
    '23':'ME',
    '24':'MD',
    '25':'MA',
    '26':'MI',
    '27':'MN',
    '28':'MS',
    '29':'MO',
    '30':'MT',
    '31':'NE',
    '32':'NV',
    '33':'NH',
    '34':'NJ',
    '35':'NM',
    '36':'NY',
    '37':'NC',
    '38':'ND',
    '39':'OH',
    '40':'OK',
    '41':'OR',
    '42':'PA',
    '44':'RI',
    '45':'SC',
    '46':'SD',
    '47':'TN',
    '48':'TX',
    '49':'UT',
    '50':'VT',
    '51':'VA',
    '53':'WA',
    '54':'WV',
    '55':'WI',
    '56':'WI',
}

state_zipcode0 = {
    'AK':   '9',
    'AL':   '3',
    'AR':   '7',
    'AZ':   '8',
    'CA':   '9',
    'CO':   '8',
    'CT':   '0',
    'DC':   '2',
    'DC':   '2',
    'DE':   '1',
    'FL':   '3',
    'GA':   '3',
    'HI':   '9',
    'IA':   '56',
    'ID':   '8',
    'IL':   '6',
    'IN':   '4',
    'KS':   '6',
    'KY':   '4',
    'LA':   '7',
    'MA':   '0',
    'MD':   '2',
    'ME':   '0',
    'MI':   '4',
    'MN':   '5',
    'MO':   '6',
    'MS':   '3',
    'MT':   '5',
    'NC':   '2',
    'ND':   '5',
    'NE':   '6',
    'NH':   '3',
    'NJ':   '0',
    'NM':   '8',
    'NV':   '8',
    'NY':   '01',
    'OH':   '4',
    'OK':   '7',
    'OR':   '9',
    'PA':   '1',
    'PR':   '0',
    'RI':   '0',
    'SC':   '2',
    'SD':   '5',
    'TN':   '3',
    'TX':   '78',
    'UT':   '8',
    'VA':   '2',
    'VT':   '0',
    'WA':   '9',
    'WI':   '5',
    'WV':   '2',
    'WY':   '8',
}

def main(data, options=OPTIONS, config=CONFIG, warning=warning):

    os.makedirs(config['cachedir'],exist_ok=True)

    if options["state_fields"]:

        # get state data
        fieldlist = []
        result = []
        for id, row in data.iterrows():
            if 'state' in data.columns:
                result.append(get_states(value=row['state']))
            elif 'latitude' in data.columns and 'longitude' in data.columns:
                pos = Point(float(row.loc['longitude']),float(row.loc['latitude']))
                result.append(get_states(contains=pos))
            else:
                raise Exception("unable to process state data without latitude and longitude columns")
        result = pandas.concat(result,ignore_index=True)
        if options['state_fields'] == '*':
            fieldlist.extend(result.columns.to_list())
        else:
            fieldlist.extend(options['state_fields'].split(','))
        for field in fieldlist:
            if field not in result.columns:
                raise Exception(f"field '{field}' is not found in state data")
            data[field] = result[field]

    if options["zipcode_fields"]:

        if not 'latitude' in data.columns or not 'longitude' in data.columns:
            raise Exception("unable to process zipcode data without latitude and longitude columns")


        # get zipcode data
        fieldlist = []
        result = []
        for id, row in data.iterrows():
            pos = Point(float(row.loc['longitude']),float(row.loc['latitude']))
            state = get_states(contains=pos)['STUSPS'][0]
            global state_zipcode0
            for digit in state_zipcode0[state]:
                result.append(get_zipcodes(digit,contains=pos))
        result = pandas.concat(result,ignore_index=True)
        if options['zipcode_fields'] == '*':
            fieldlist.extend(result.columns.to_list())
        else:
            fieldlist.extend(options['zipcode_fields'].split(','))
        for field in fieldlist:
            if field not in result.columns:
                raise Exception(f"field '{field}' is not found in zipcode data")
            data[field] = result[field]

    if options["tract_fields"]:

        warning("census tract is not implemented yet")
        return data

    return data

state_data = None
def get_states(match="STUSPS",value=None,contains=None,config=CONFIG):
    """Get state geodata
    Return the state matching the specified search parameters.
    If only "value" is given, then the state with that USPS abbreviation is
    returned.  If "match" is given, then "value" is matched to the specified
    column.  If "contains" is provided, then "value" and "match" are ignored and
    the state containing the specified "Point(longitude,latitude)" is returned.
    If both "value" and "contains" are "None" then all states are returned.
    ARGUMENTS:
        match (str)        Column that must match the value given
        value (str)        Value that must match the specified column
        contains (Point)   Point (lon,lat) contained by the states
        config (dict)      Configuration data
            "urladdr"         URL from which state geodata is obtained
            "cachedir"        local cache dir for downloaded geodata
    RETURNS:
        DataFrame   Geopandas dataframe containing state geodata
    """
    global state_data
    if type(state_data) == type(None):
        states_url = f"{config['urladdr']}/STATE/{config['states_filename']}"
        states_file = f"{config['cachedir']}/states"

        if not os.path.exists(states_file+".zip"):

            # TODO: manage multiple simultaneous requests, i.e., wait for download to finish
            # download from TIGER repo
            with urllib.request.urlopen(states_url) as resp, open(states_file+".zip", "wb") as f:
                try:
                    f.write(resp.read())
                except:
                    os.remove(states_file)

        if not os.path.exists(f"{states_file}.gdf"):

            # cache file is not available
            state_data = geopandas.read_file(f"zip://{states_file}.zip")
            with open(f"{states_file}.gdf","wb") as f: pickle.dump(state_data,f)

        else:

            # cache file is available
            with open(f"{states_file}.gdf","rb") as f: state_data = pickle.load(f)

    if contains:

        # search based on Point
        return state_data[state_data.contains(contains)].reset_index()

    elif value:

        # search based on matched value (by default STUSPS)
        return state_data[state_data[match]==value].reset_index()

    else:

        # no search - return everything
        return state_data

zipcode_data = None
def get_zipcodes(zipcode=None,contains=None,config=CONFIG):
    """Get zipcode geodata
    """
    global zipcode_data
    if type(zipcode_data) == type(None):

        zipcode_url = f"{config['urladdr']}/ZCTA5/{config['zipcode_filename']}"
        zipcode_file = f"{config['cachedir']}/zipcodes"

        if not os.path.exists(zipcode_file+".zip"):

            # TODO: manage multiple simultaneous requests, i.e., wait for download to finish
            # download from TIGER repo
            with urllib.request.urlopen(zipcode_url) as resp, open(zipcode_file+".zip", "wb") as f:
                try:
                    f.write(resp.read())
                except:
                    os.remove(zipcode_file)

        if zipcode != None:

            # regional zipcode file is ok to use
            digit = str(zipcode)[0]
            if not os.path.exists(f"{zipcode_file}{digit}.gdf"):

                # cache file is not available
                zipcode_data = geopandas.read_file(f"zip://{zipcode_file}.zip")
                zipcode_data = zipcode_data[zipcode_data["GEOID10"].str[0]==digit]
                with open(f"{zipcode_file}{digit}.gdf","wb") as f: pickle.dump(zipcode_data,f)
            else:

                # cache file is available
                with open(f"{zipcode_file}{digit}.gdf","rb") as f: zipcode_data = pickle.load(f)

        else:

            # must use national zipcode file
            if not os.path.exists(f"{zipcode_file}.gdf"):

                # cache file is not available
                zipcode_data = geopandas.read_file(f"zip://{zipcode_file}.zip")
                with open(f"{zipcode_file}.gdf","wb") as f: pickle.dump(zipcode_data,f)

            else:

                # cache file is available
                with open(f"{zipcode_file}.gdf","rb") as f: zipcode_data = pickle.load(f)

    if contains:

        # search for zipcode based on geopandas Point
        result = zipcode_data[zipcode_data.contains(contains)].reset_index()

    elif zipcode:

        # search for zipcode based on zipcode given
        result = zipcode_data[zipcode_data["GEOID10"].str.startswith(str(zipcode))].reset_index()
    else:

        # no search - return everything
        result = zipcode_data

    # with open(f"{config['cachedir']}/zipcode_result.last","w") as f: pickle.dump(result,f)

    return result


if __name__ == "__main__":
    DATA = None
    load_config()
    result = main(DATA)
    result.to_csv(f"{OPENFIDO_OUTPUT}/address.csv")
