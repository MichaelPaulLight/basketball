data {
  int<lower=1> N_shots;              // Number of shots
  int<lower=1> N_defenders;          // Number of unique defenders
  int<lower=1> N_periods;            // Number of periods (4)
  
  // Play by play data
  int<lower=1, upper=N_defenders> defenders[N_shots, 5];  // 5 defenders per shot
  int<lower=1, upper=N_periods> period[N_shots];          // Period for each shot
  int<lower=0, upper=1> shot_made[N_shots];              // Whether shot was made (1) or missed (0)
  
  // Defender dashboard aggregates
  int<lower=0> def_shots[N_defenders, N_periods];     // Number of shots defended
  int<lower=0> def_makes[N_defenders, N_periods];     // Number of makes when defending
}

parameters {
  // Probability each defender was closest for each shot
  simplex[5] theta[N_shots];  // 5 dimensions since 5 defenders per shot
}

model {
  // Prior 
  for (n in 1:N_shots) {
    theta[n] ~ dirichlet(rep_vector(2.0, 5));
  }
  
  // Likelihood
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      // Expected number of total shots and makes for this defender in this period
      real exp_shots = 0;
      real exp_makes = 0;
      
      // Sum up probability this defender was closest across relevant shots
      for (n in 1:N_shots) {
        if (period[n] == p) {  // Only include shots from this period
          for (pos in 1:5) {
            if (defenders[n,pos] == d) {
              exp_shots += theta[n,pos];
              exp_makes += theta[n,pos] * shot_made[n];  // Only add to makes if shot went in
            }
          }
        }
      }
      
      // Compare to reported totals
      def_shots[d,p] ~ poisson(exp_shots);
      def_makes[d,p] ~ poisson(exp_makes);
    }
  }
}

generated quantities {
  // Most likely closest defender for each shot
  int closest_defender[N_shots];
  
  // Expected shots/makes defended under current parameters
  matrix[N_defenders, N_periods] exp_shots;
  matrix[N_defenders, N_periods] exp_makes;
  
  // Field goal percentage against each defender
  matrix[N_defenders, N_periods] exp_fg_pct;
  
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
  
  // Calculate expected shots/makes and FG%
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      exp_shots[d,p] = 0;
      exp_makes[d,p] = 0;
      
      for (n in 1:N_shots) {
        if (period[n] == p) {
          for (pos in 1:5) {
            if (defenders[n,pos] == d) {
              exp_shots[d,p] += theta[n,pos];
              exp_makes[d,p] += theta[n,pos] * shot_made[n];
            }
          }
        }
      }
      
      // Calculate expected FG% (with protection against divide by zero)
      exp_fg_pct[d,p] = exp_shots[d,p] > 0 ? exp_makes[d,p] / exp_shots[d,p] : 0;
    }
  }
}

