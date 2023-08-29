import json
import os
import pandas as pd
import numpy as np



def load_data_it20(path_to_json):
    # This function loads all of the json files and stores them as items in a list
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    data = []
    for k in range(len(json_files)):
        str1 = 't20s_male_json/' + json_files[k]
        with open(str1) as f:
            
            match1 = json.load(f)
            match_id = json_files[k][: -5]
            match1['match id'] = match_id
            data.append(match1)
    return data

def load_data_ipl(path_to_json):
    # This function loads all of the json files and stores them as items in a list
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    data = []
    for k in range(len(json_files)):
        str1 = 'ipl_json/' + json_files[k]
        with open(str1) as f:
            
            match1 = json.load(f)
            match_id = json_files[k][: -5]
            match1['match id'] = match_id
            data.append(match1)
    return data

def create_df(data):
    X = []
    
    for j in range(len(data)):
        if len(data[j]['innings']) > 1:
            if 'winner' in data[j]['info']['outcome'].keys():
                if 'target' in data[j]['innings'][1].keys():
                    # Need to ensure that the data has a winner and a target score as we are not interested in incomplete matched
                    match_id = data[j]['match id']
                    date = data[j]['info']['dates'][0]
                    match_target = data[j]['innings'][1]['target']['runs']
                    venue = data[j]['info']['venue']
                    chaser = data[j]['innings'][1]['team']
                    bat_first = data[j]['innings'][0]['team']
                    
                    winner = data[j]['info']['outcome']['winner']
                    chase_success = 0
                    if chaser == winner:
                        chase_success = 1
                    # Store match specific data such as team names, date, winner, first innings score and initialise chase success feature
                    for innings in range(len(data[j]['innings'])):
                        n_wickets = 0
                        team_runs = 0
                        balls_rem = 120
                        
                        for over in range(len(data[j]['innings'][innings]['overs'])):
                            for ball in range(len(data[j]['innings'][innings]['overs'][over]['deliveries'])):
                                ball_in_over = 120-balls_rem-(6*over)
                                batter = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['batter']
                                non_striker = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['non_striker']
                                bowler = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['bowler']
                                batter_runs = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['runs']['batter']
                                extra_runs = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['runs']['extras']
                                total_runs = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['runs']['total']
                                
                                # For each ball of the game, extract the important information
                                team_runs += total_runs
                                wicket = 0
                                method = 'N/A'
                                player_out = 'N/A'
                                if 'wickets' in data[j]['innings'][innings]['overs'][over]['deliveries'][ball].keys():
                                    wicket = 1
                                    n_wickets += 1
                                    method = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['wickets'][0]['kind']
                                    player_out = data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['wickets'][0]['player_out']
                              

                                if innings == 1:
                                    runs_to_target = match_target - team_runs
                                else:
                                    runs_to_target = 'N/A'
                                
                                if 'extras' in data[j]['innings'][innings]['overs'][over]['deliveries'][ball].keys():
                                    extra_type = list(data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['extras'].keys())
                                    if 'wides' in data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['extras']:
                                        # Initialise a feature which represents whether or not a ball had to be rebowled, this will be useful later
                                        rebowled = 1  
                                    elif 'noballs' in data[j]['innings'][innings]['overs'][over]['deliveries'][ball]['extras']:
                                        rebowled = 1  
                                    else:
                                        rebowled = 0
                                        balls_rem -= 1
                                else:
                                    extra_type = []
                                    rebowled = 0
                                    balls_rem -= 1
                                X.append([match_id, date, venue, bat_first,  chaser, innings+1, over+1, ball_in_over+1, batter, non_striker, bowler, batter_runs, extra_runs, total_runs, rebowled, extra_type, wicket, method, player_out, team_runs, n_wickets, match_target, runs_to_target, balls_rem, winner, chase_success])
    columns = ['Match ID','Date', 'Venue', 'Bat First', 'Bat Second','Innings', 'Over', 'Ball', 'Batter','Non Striker', 'Bowler', 'Batter Runs', 'Extra Runs', 'Runs From Ball','Ball Rebowled', 'Extra Type', 'Wicket', 'Method', 'Player Out', 'Innings Runs', 'Innings Wickets', 'Target Score', 'Runs to Get','Balls Remaining', 'Winner', 'Chased Successfully']
    # Createw a data frame with the ball by ball data extracted, column names are given above
    df = pd.DataFrame(X, columns = columns)
    # create a new column to store the sum of Batter Runs
    df['Total Batter Runs'] = 0
    # create a new column to store the sum of Non Striker Runs
    df['Total Non Striker Runs'] = 0
    # Create new columns called 'batter balls faced' and 'non striker balls faced'
    df['Batter Balls Faced'] = 0
    df['Non Striker Balls Faced'] = 0
    # Create new columns for the case when a player gets out to give their final runs total and balls faced total
    df['Player Out Runs'] = 'N/A'
    df['Player Out Balls Faced'] = 'N/A'

    df['Bowler Runs Conceded'] = df.apply(
    lambda row: row['Batter Runs'] + row['Extra Runs'] 
    if any(item in row['Extra Type'] for item in ['wides', 'noballs'])
    else row['Batter Runs'], axis=1)

    # loop over each row in the data frame
    for i, row in df.iterrows():
        batter = row['Batter']
        date = row['Date']
        non_striker = row['Non Striker']
        
        # get the rows to iterate over, capped at 200 rows
        start_index = max(0, i - 200)
        end_index = i + 1
        rows_to_iterate = df.iloc[start_index:end_index]
        
        total_batter_runs = rows_to_iterate.loc[(rows_to_iterate['Batter'] == batter) & (rows_to_iterate['Date'] == date), 'Batter Runs'].sum()
        total_non_striker_runs = rows_to_iterate.loc[(rows_to_iterate['Batter'] == non_striker) & (rows_to_iterate['Date'] == date), 'Batter Runs'].sum()
        # store the total runs for the batter and date in the new column
        df.at[i, 'Total Batter Runs'] = total_batter_runs
        df.at[i, 'Total Non Striker Runs'] = total_non_striker_runs
        
        
        # Initialize a list to keep track of the unique balls faced
        unique_balls_faced_batter = []
        unique_balls_faced_non_striker = []
        
        # Loop through the rows above the current row (up to a cap of 200 rows)
        for j in range(max(0, i - 200), i + 1):

            # Check if the batter and date match the current row
            if df.at[j, 'Batter'] == batter and df.at[j, 'Date'] == date:
                
                # Add the balls remaining to the list of unique balls faced
                unique_balls_faced_batter.append(df.at[j, 'Balls Remaining'])
            # Check if the batter and date match the current row
            if df.at[j, 'Batter'] == non_striker and df.at[j, 'Date'] == date:
                
                # Add the balls remaining to the list of unique balls faced
                unique_balls_faced_non_striker.append(df.at[j, 'Balls Remaining'])
            
        
        # Set the value of the 'batter balls faced' column for the current row to the number of unique balls faced
        df.at[i, 'Batter Balls Faced'] = len(set(unique_balls_faced_batter))
        df.at[i, 'Non Striker Balls Faced'] = len(set(unique_balls_faced_non_striker))


    for i, row in df.iterrows():
        if row['Batter Balls Faced'] == 1:
            if df.at[i, 'Ball'] == df.at[i+1, 'Ball']:
                
                df.at[i, 'Batter Balls Faced'] = 0
        if row['Wicket'] == 1:
            if row['Player Out'] == row['Batter']:
                # Add the final stats for the out batter and then set the no of runs and balls faced to 0
                df['Player Out Runs'].iloc[i] = df.at[i, 'Total Batter Runs']
                df['Player Out Balls Faced'].iloc[i] = df.at[i, 'Batter Balls Faced']
                df.at[i, 'Total Batter Runs'] = 0
                df.at[i, 'Batter Balls Faced'] = 0
            elif row['Player Out'] == row['Non Striker']:
                # Add the final stats for the out batter and then set the no of runs and balls faced to 0
                df['Player Out Runs'].iloc[i] = df.at[i, 'Total Non Striker Runs']
                df['Player Out Balls Faced'].iloc[i] = df.at[i, 'Non Striker Balls Faced']
                df.at[i, 'Total Non Striker Runs'] = 0
                df.at[i, 'Non Striker Balls Faced'] = 0

    df['Valid Ball'] = (df['Ball Rebowled'] != 1).astype(int)

    return df

# Uncomment the lines below to recreate csv file for IT20 data
path_to_json = '/Users/jamiewelsh/Python/Cric/CricketDataAnalysis/t20s_male_json/'
it20_data = create_df(load_data_it20(path_to_json))  
it20_data.to_csv('ball_by_ball_it20.csv', index=False)
print('IT20 done')

# Uncomment the lines below to recreate csv file for IPL data
path_to_json = '/Users/jamiewelsh/Python/Cric/CricketDataAnalysis/ipl_json/'
ipl_data = create_df(load_data_ipl(path_to_json))  
ipl_data.to_csv('ball_by_ball_ipl.csv', index=False)



