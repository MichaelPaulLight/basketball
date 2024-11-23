data {
  int<lower=1> N;  // number of shots
  int<lower=1> K;  // number of defenders
  int<lower=1> T;  // number of periods
  int<lower=0,upper=1> y[N];  // shot outcomes
  int<lower=1,upper=K> d[N,5];  // 5 defenders for each shot
  int<lower=1,upper=T> t[N];  // period for each shot
  
  // Aggregated data
  int<lower=0> makes[K,T];  // makes by defender and period
  int<lower=0> misses[K,T];  // misses by defender and period
}

parameters {
  real<lower=0,upper=1> theta[K];  // defender-specific FG% allowed
  simplex[5] pi;  // probability of being closest defender (position-based)
  real<lower=0> sigma;  // variation in defensive ability
}

model {
  // Priors
  theta ~ beta(2,2);
  pi ~ dirichlet(rep_vector(2.0, 5));
  sigma ~ exponential(1);
  
  // Likelihood for shot outcomes
  for (i in 1:N) {
    vector[5] lp;  // log probabilities for each defender being closest
    
    for (j in 1:5) {
      int defender = d[i,j];
      lp[j] = log(pi[j]) + normal_lpdf(y[i] | theta[defender], sigma);
    }
    
    target += log_sum_exp(lp);  // marginalize over defender assignment
  }
  
  // Likelihood for aggregated data
  for (k in 1:K) {
    for (t in 1:T) {
      makes[k,t] ~ binomial(makes[k,t] + misses[k,t], theta[k]);
    }
  }
}

generated quantities {
  // Infer most likely closest defender for each shot
  int<lower=1,upper=5> z[N];
  for (i in 1:N) {
    vector[5] lp;
    for (j in 1:5) {
      int defender = d[i,j];
      lp[j] = log(pi[j]) + normal_lpdf(y[i] | theta[defender], sigma);
    }
    z[i] = categorical_rng(softmax(lp));
  }
}
