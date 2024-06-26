# Tropical Storm Potential Intensity Predictor (Bermuda)
## Version 0.2.0

Runs calculations for potential maximum wind speed, minimum pressure (at eye of storm) and outflow temperature given a date, sea level pressure and ocean sample depth.

## How it works

Inputs are provided as command-line arguments when running pi_predictions.py. Python script makes a request to a REST API. The REST API requests atmospheric sounding data from the University of Wyoming and ocean temperature data from ocean gliders and research cruises.

The REST API then sends a request to a PI REST API where the data is run through a PI Model Python script. Results are then sent back to the Python frontend for outputting.

Outputs are stored to a CSV file and full logs containing all data and metadata used is stored to a JSON file within a logs folder

## Getting Started

### Dependencies

- Python v3.9+
- pytz v2021.3
- requests v2.26+

### Installing

Simply clone this repository to your machine and run

```
pip3 install -r /path/to/requirements.txt
```

using the path to requirements.txt within your cloned repository.

### Executing program

- Run pi_predictions.py passing sea level pressure as a command line argument, and any other additional arguments (see below)

Example command:

#### Using top 50m layer
```
python3 pi_predictions.py -d 2024060412 -p 1020 -t t50
```

#### Using sea surface temperature
```
python3 pi_predictions.py -d 2024060412 -p 1020 -t sst
```

#### Using manual ocean temperature input
```
python3 pi_predictions.py -d 2024060412 -p 1020 -t 24.6
```

#### Command-line arguments

    -d datetime (YYYYMMDDHH)
    -t Ocean sample depth ('tX' where X is layer depth or 'sst' or 'X' where X is ocean temperature)
    -p sea level pressure (mb)
    -o CSV output path (path/to/output/file/your_file_name.csv)

## Help

Run this command for a list of optional command-line arguments

```
python3 pi_predictions.py --help
```

## Authors

 - Jake Hallam - *Code development & maintenance*
[ja.hallam11@gmail.com](mailto:ja.hallam11@gmail.com)
 - Samantha Hallam, PhD - *Model research & development* [samantha.hallam@mu.ie](mailto:samantha.hallam@mu.ie)

## Version History

 - 0.1.0-alpha - Initial prototype release (Alpha)
 - 0.2.0 - 10/06/2024 - Support for manual ocean temperature input
   

## Acknowledgments

 - Model based on research from Hallam, Samantha, et al. "Increasing tropical cyclone intensity and potential intensity in the subtropical Atlantic around Bermuda from an ocean heat content perspective 1955–2019." Environmental Research Letters 16.3 (2021): 034052. DOI 10.1088/1748-9326/abe493
 - Program utilises pyPI from Daniel Gilford to calculate minimum pressure
Gilford, D. M. 2020: pyPI: Potential Intensity Calculations in Python, v1.2, Zenodo, doi:10.5281/zenodo.3900548
