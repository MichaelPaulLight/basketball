Date := $(shell date +%Y-%m-%d)
OLD_FILE := data/250203_pbp_gt.parquet
dashboards = data/$(Date)_defender_dashboard.parquet data/$(Date)_closest_defender_shooting_dashboard.parquet data/$(Date)_closest_defender_shooting_dash_10_plus.parquet

#data/new_pbp_$(Date).parquet: pbp_data_initial.py $(OLD_FILE)
#	python pbp_data_initial.py $(OLD_FILE) data/new_pbp_$(Date).parquet

#data/$(Date)_combined_pbp.parquet: data_cleaning.r $(OLD_FILE)
#	Rscript data_cleaning.r $(OLD_FILE) data/$(Date)_combined_pbp.parquet


$(dashboards): dashboard_update.r data/closest_defender_shooting_dashboard.parquet data/closest_defender_shooting_dash_10_plus.parquet data/defender_dashboard.parquet
	Rscript dashboard_update.r data/closest_defender_shooting_dashboard.parquet data/closest_defender_shooting_dash_10_plus.parquet data/defender_dashboard.parquet $(dashboards)
