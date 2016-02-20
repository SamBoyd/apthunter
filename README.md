Requirements: Python 2.7 and NodeJs v.0.12+

in the main folder: install Python dependencies with

`pip install -t requirements.txt`

configure your parameters in `apthunter/config.py` (some are magic, it is setup to search in the radius of the office)

then crawl
`./crawl.sh`

now we need to find dupes
`./find_dupes.sh`

finally, generate the final data file
`./build_data.sh`
`cd site`
`brunch watch --server`

on localhost:3333 you'll find an openstreetmap with all your lovely choices!

