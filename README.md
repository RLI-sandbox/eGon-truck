# eGon-truck

This repository is part of the [eGon-data](https://github.com/openego/eGon-data) workflow.
It uses open data from [automatic metering stations on freeways and federal highways](https://www.bast.de/DE/Verkehrstechnik/Fachthemen/v2-verkehrszaehlung/zaehl_node.html) (as of 2019) from [BASt (Bundesanstalt für Straßenwesen)](https://www.bast.de/DE/Home/home_node.html;jsessionid=F82FF1B81A7C5DED90D5951E666D87A9.live21321) to estimate the hydrogen demand per mv grid district from heavy goods vehicle traffic (HGV traffic) in future scenarios.

## Assumptions

The ramp-up figures are taken from [Scenario C 2035 Grid Development Plan 2021-2035](https://www.netzentwicklungsplan.de/sites/default/files/paragraphs-files/NEP_2035_V2021_2_Entwurf_Teil1.pdf). 
According to this, 100,000 e-trucks are expected in Germany in 2035, each covering an average of 100,000 km per year.
In the context of the eGon project, it is assumed that e-trucks will be completely hydrogen-powered.

The hydrogen consumption is assumed to be 6.68 kgH2 per 100 km with an additional [supply chain leakage rate of 0.5 %](https://www.energy.gov/eere/fuelcells/doe-technical-targets-hydrogen-delivery).

Assumptions can be changed within the [config/settings.toml](https://github.com/RLI-sandbox/eGon-truck/blob/main/config/settings.toml).

## Methodology

Using a Voronoi interpolation, the censuses of the BASt data is distributed according to the area fractions of the Voronoi fields within each mv grid.
