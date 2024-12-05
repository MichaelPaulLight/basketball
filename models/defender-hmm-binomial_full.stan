data {
  int<lower=1> N;              // Number of shots
  int<lower=1> n_defender_name;          // Number of unique defenders
  int<lower=1> n_period;            // Number of periods
  int<lower=1> n_shot_type;         // Number of shot types (2: 2pt/3pt)
  int<lower=1> n_defense_category;     // Number of defense categories
  
  // Play by play data
  array[N, 5] int<lower=1, upper=n_defender_name> defender_name;  // 5 defenders per shot
  array[N] int<lower=1, upper=n_period> period; // Period for each shot
  array[N] int<lower=1, upper=n_shot_type> shot_type; // Shot type for each shot
  array[N] int<lower=1, upper=n_defense_category> defense_category; // Defense category for each shot
  array[N] int<lower=0, upper=1> shot_made_flag; // Whether shot was made (1) or missed (0)
  
  // Defender dashboard aggregates - reshaped version
  array[n_defender_name, n_period, n_shot_type, n_defense_category] int<lower=0> makes; // Number of makes
  array[n_defender_name, n_period, n_shot_type, n_defense_category] int<lower=0> misses; // Number of misses

  // For shots with known defenders
  array[N] int<lower=0, upper=1> known_defender_indicator;  // Indicator if shot has known defender
  array[N] int<lower=1, upper=5> known_defender_pos;  // Position (1-5) of known defender in defenders array

  // Hyperparameters
  real<lower=0> alpha_known;     // e.g. 1000.0
  real<lower=0> alpha_unknown;   // e.g. 0.001
  real<lower=0> alpha_regular;   // e.g. 2.0
}

parameters {
  // Probability each defender was closest for each shot
  array[N] simplex[5] theta; // 5 dimensions since 5 defenders per shot
}

transformed parameters {
  // Calculate expected shots and makes for each defender-period-type-category combination
  array[n_defender_name, n_period, n_shot_type, n_defense_category] real exp_shots;
  array[n_defender_name, n_period, n_shot_type, n_defense_category] real exp_makes;
  
  // Initialize arrays
  for (d in 1:n_defender_name) {
    for (p in 1:n_period) {
      for (s in 1:n_shot_type) {
        for (c in 1:n_defense_category) {
          exp_shots[d,p,s,c] = 0;
          exp_makes[d,p,s,c] = 0;
        }
      }
    }
  }
  
  // Calculate expectations
  for (n in 1:N) {
    for (pos in 1:5) {
      int d = defender_name[n,pos];
      int p = period[n];
      int s = shot_type[n];
      int c = defense_category[n];
      
      exp_shots[d,p,s,c] += theta[n,pos];
      exp_makes[d,p,s,c] += theta[n,pos] * shot_made_flag[n];
    }
  }
}

model {
  // Prior on theta
  for (n in 1:N) {
    if (known_defender_indicator[n]) {
      // Use very large concentration parameters to force probability near 1.0
      vector[5] alpha = rep_vector(0.001, 5);
      alpha[known_defender_pos[n]] = 1000.0;  // Very large value
      theta[n] ~ dirichlet(alpha);
    } else {
      // Regular prior for unknown cases
      theta[n] ~ dirichlet(rep_vector(2.0, 5));
    }
  }
  
  // Likelihood
  for (d in 1:n_defender_name) {
    for (p in 1:n_period) {
      for (s in 1:n_shot_type) {
        for (c in 1:n_defense_category) {
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
  array[N] int closest_defender;
  
  // Expected FG% for each defender-period-type-category combination
  array[n_defender_name, n_period, n_shot_type, n_defense_category] real exp_fg_pct;
  
  // Calculate closest defenders
  for (n in 1:N) {
    int max_pos = 1;
    real max_prob = theta[n,1];
    
    for (pos in 2:5) {
      if (theta[n,pos] > max_prob) {
        max_pos = pos;
        max_prob = theta[n,pos];
      }
    }
    
    closest_defender[n] = defender_name[n,max_pos];
  }
  
  // Calculate expected FG%
  for (d in 1:n_defender_name) {
    for (p in 1:n_period) {
      for (s in 1:n_shot_type) {
        for (c in 1:n_defense_category) {
          exp_fg_pct[d,p,s,c] = exp_shots[d,p,s,c] > 0 ? 
            exp_makes[d,p,s,c] / exp_shots[d,p,s,c] : 0;
        }
      }
    }
  }
}