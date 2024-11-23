data {
  int<lower=1> N_shots;              // Number of shots
  int<lower=1> N_defenders;          // Number of unique defenders
  int<lower=1> N_periods;            // Number of periods (4)
  
  // Play by play data
  int<lower=1, upper=N_defenders> defenders[N_shots, 5];  // 5 defenders per shot
  int<lower=1, upper=N_periods> period[N_shots];          // Period for each shot
  
  // Defender dashboard aggregates - total shots defended per period
  int<lower=0> def_shots[N_defenders, N_periods];     // Number of shots defended
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
  
  // Likelihood - total shots constraints
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      // Expected number of shots defended by this defender in this period
      real exp_shots = 0;
      
      // Sum up probability this defender was closest across relevant shots
      for (n in 1:N_shots) {
        if (period[n] == p) {  // Only include shots from this period
          for (pos in 1:5) {
            if (defenders[n,pos] == d) {
              exp_shots += theta[n,pos];
            }
          }
        }
      }
      
      // Compare to reported total
      def_shots[d,p] ~ poisson(exp_shots);
    }
  }
}

generated quantities {
  // Most likely closest defender for each shot
  int closest_defender[N_shots];
  
  // Expected shots defended under current parameters
  matrix[N_defenders, N_periods] exp_shots;
  
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
  
  // Calculate expected shots
  for (d in 1:N_defenders) {
    for (p in 1:N_periods) {
      exp_shots[d,p] = 0;
      for (n in 1:N_shots) {
        if (period[n] == p) {
          for (pos in 1:5) {
            if (defenders[n,pos] == d) {
              exp_shots[d,p] += theta[n,pos];
            }
          }
        }
      }
    }
  }
}

