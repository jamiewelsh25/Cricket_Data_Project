# CricketDataAnalysis

This project will explore trends in T20 data. 

* The analysis.ipynb contains some exploratory data analysis of the International T20 ball-by-ball dataset. A framework is designed to score and rank batters, bowlers and all-rounders based purely on performance data by considering the runs added over the average batter and the runs reduced compared to the average bowler.
* The analysis_ipl.ipynb notebook is a carbon copy of the previous notebook except it looks at the IPL ball-by-ball data.
* The chase_predictor_it20.ipynb notebook contains predictive models for either IPL of IT20 to determine chase success. The models are trained on data pre 2018 and evaluated on data from 2018 onwards. The logistic regression classifier predicts chase success with an accuracy of around 82%.
* The target_predictor_it20.ipynb notebook sees machine learning models trained to predict a frist innings target score given the current state of play (trained on the T20 International dataset) The XGBoost regressor yields an MSE of 714 on the unseen data with weak predictive performance early in an innings.
* The chase_predictor_ipl.ipynb and target_predictor_ipl.ipynb are almsot identical to the equivalent _it20.ipynb notebooks however they are trained on the IPL data. This leads to better prediction of target scores but worse prediction of chase success. I experimented with combining the datasets but this worsened performance.

These notebooks could be generalised to ODI or test data with little difficulty. 


