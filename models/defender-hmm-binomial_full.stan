data {
  int<lower=1> N_shots;              // Number of shots
  int<lower=1> N_defenders;          // Number of unique defenders
  int<lower=1> N_periods;            // Number of periods
  int<lower=1> N_shot_types;         // Number of shot types (2: 2pt/3pt)
  int<lower=1> N_def_categories;     // Number of defense categories
  
  // Play by play data
  int<lower=1, upper=N_defenders> defenders[N_shots, 5];  // 5 defenders per shot
  int<lower=1, upper=N_periods> period[N_shots];          // Period for each shot
  int<lower=1, upper=N_shot_types> shot_type[N_shots];    // Shot type for each shot
  int<lower=1, upper=N_def_categories> def_category[N_shots];   // Defense category for each shot
  int<lower=0, upper=1> shot_made[N_shots];              // Whether shot was made (1) or missed (0)
  
  // Defender dashboard aggregates - reshaped version
  int<lower=0> makes[N_defenders, N_periods, N_shot_types, N_def_categories];     // Number of makes
  int<lower=0> misses[N_defenders, N_periods, N_shot_types, N_def_categories];    // Number of misses
  
  // For shots with known defenders
  int<lower=0, upper=1> has_known_defender[N_shots];  // Indicator if shot has known defender
  int<lower=1, upper=5> known_defender_pos[N_shots];  // Position (1-5) of known defender in defenders array
}

parameters {
  // Probability each defender was closest for each shot
  simplex[5] theta[N_shots];  // 5 dimensions since 5 defenders per shot
}

transformed parameters {
  // Calculate expected shots and makes for each defender-period-type-category combination
  array[N_defenders, N_periods, N_shot_types, N_def_categories] real exp_shots;
  array[N_defenders, N_periods, N_shot_types, N_def_categories] real exp_makes;
  
  // Initialize arrays
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      for (s in 1:N_shot_types) {
        for (c in 1:N_def_categories) {
          exp_shots[d,p,s,c] = 0;
          exp_makes[d,p,s,c] = 0;
        }
      }
    }
  }
  
  // Calculate expectations
  for (n in 1:N_shots) {
    for (pos in 1:5) {
      int d = defenders[n,pos];
      int p = period[n];
      int s = shot_type[n];
      int c = def_category[n];
      
      exp_shots[d,p,s,c] += theta[n,pos];
      exp_makes[d,p,s,c] += theta[n,pos] * shot_made[n];
    }
  }
}

model {
  // Prior on theta - different for known vs unknown defenders
  for (n in 1:N_shots) {
    if (has_known_defender[n]) {
      // For known defenders, force probability=1 for the known defender
      theta[n] = rep_vector(0.0, 5);
      theta[n, known_defender_pos[n]] = 1.0;
    } else {
      // For unknown defenders, use dirichlet prior as before
      theta[n] ~ dirichlet(rep_vector(2.0, 5));
    }
  }
  
  // Likelihood
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      for (s in 1:N_shot_types) {
        for (c in 1:N_def_categories) {
          // Total shots constraint
          int total_shots = makes[d,p,s,c] + misses[d,p,s,c];
          total_shots ~ poisson(exp_shots[d,p,s,c]);
          
          // Makes given total shots
          if (total_shots > 0) {  // Only model makes if there were shots
            makes[d,p,s,c] ~ binomial(total_shots, exp_makes[d,p,s,c] / exp_shots[d,p,s,c]);
          }
        }
      }
    }
  }
}

generated quantities {
  // Most likely closest defender for each shot
  int closest_defender[N_shots];
  
  // Expected FG% for each defender-period-type-category combination
  array[N_defenders, N_periods, N_shot_types, N_def_categories] real exp_fg_pct;
  
  // Calculate closest defenders
  for (n in 1:N_shots) {
    int max_pos = 1;
    real max_prob = theta[n,1];
    
    for (pos in 2:5) {
      if (theta[n,pos] > max_prob) {
        max_pos = pos;
        max_prob = theta[n,pos];
      }
    }
    
    closest_defender[n] = defenders[n,max_pos];
  }
  
  // Calculate expected FG%
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      for (s in 1:N_shot_types) {
        for (c in 1:N_def_categories) {
          exp_fg_pct[d,p,s,c] = exp_shots[d,p,s,c] > 0 ? 
            exp_makes[d,p,s,c] / exp_shots[d,p,s,c] : 0;
        }
      }
    }
  }
}