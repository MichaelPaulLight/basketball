data {
  // For one shot
  int<lower=1> N_defenders;          // Number of defenders (5)
  int<lower=1, upper=N_defenders> defenders[5];  // IDs of the 5 defenders
}

parameters {
  // Probability each defender was closest for this shot
  simplex[5] theta;  // Must sum to 1
}

model {
  // Prior
  theta ~ dirichlet(rep_vector(2.0, 5));  // Weakly informative prior suggesting roughly equal probabilities
}

generated quantities {
  // Most likely closest defender
  int closest_defender;
  {
    int max_pos = 1;
    real max_prob = theta[1];
    
    for (pos in 2:5) {
      if (theta[pos] > max_prob) {
        max_pos = pos;
        max_prob = theta[pos];
      }
    }
    
    closest_defender = defenders[max_pos];
  }
}

