Date := $(shell date +%Y-%m-%d)
OLD_FILE := data/250203_pbp_gt.parquet
dashboards = data/$(Date)_defender_dashboard.parquet data/$(Date)_closest_defender_shooting_dashboard.parquet data/$(Date)_closest_defender_shooting_dash_10_plus.parquet
#$Formatted_Data := 

#Pass in the model to be displayed in shiny app
shiny_app: shinystan.r data/$(Date)_fit_model.rds
	Rscript shinystan.r data/$(Date)_fit_model.rds

#Heirachal Clustering and Dendogram
#data/$(Date)_dendogram.png: Clustering Dendogram.py $(Formatted_Data)
#	Python Clustering Dendogram.py $(Formatted_Data) data/$(Date)_dendogram.png

#Now input dashboards, to be formatted and then modeled
data/$(Date)_fit_model.rds: GenerateModel.r data/$(Date)_combined_pbp.parquet $(dashboards)
	Rscript GenerateModel.r data/$(Date)_combined_pbp.parquet $(dashboards) data/$(Date)_fit_model.rds

#Once issue with the date is resolved, this can be uncommented
#$(dashboards): dashboard_update.r data/closest_defender_shooting_dashboard.parquet data/closest_defender_shooting_dash_10_plus.parquet data/defender_dashboard.parquet
#	Rscript dashboard_update.r data/closest_defender_shooting_dashboard.parquet data/closest_defender_shooting_dash_10_plus.parquet data/defender_dashboard.parquet $(dashboards)

data/$(Date)_combined_pbp.parquet: data_cleaning.r $(OLD_FILE)
	Rscript data_cleaning.r $(OLD_FILE) data/$(Date)_combined_pbp.parquet

#data/new_pbp_$(Date).parquet: pbp_data_initial.py $(OLD_FILE)
#	python pbp_data_initial.py $(OLD_FILE) data/new_pbp_$(Date).parquet






