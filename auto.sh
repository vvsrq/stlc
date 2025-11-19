#!/usr/bin/env bash
sumo -c baseline.sumocfg --tripinfo-output baseline_tripinfo_multi.xml --emission-output baseline_emissions_multi.xml --queue-output baseline_queue_multi.xml

python3 /opt/homebrew/opt/sumo/share/sumo/tools/xml/xml2csv.py baseline_tripinfo_multi.xml
python3 /opt/homebrew/opt/sumo/share/sumo/tools/xml/xml2csv.py baseline_emissions_multi.xml
python3 /opt/homebrew/opt/sumo/share/sumo/tools/xml/xml2csv.py baseline_queue_multi.xml

python3 proccess_data.py