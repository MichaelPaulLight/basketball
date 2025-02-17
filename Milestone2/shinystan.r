install.packages('shinystan')
library(shinystan)
install.packages('rsconnect')
library(rsconnect)
install.packages(c('ggplot2', 'shiny'))
library(ggplot2)
library(shiny)

#Line Below for online deployment
#rsconnect::setAccountInfo(name="<ACCOUNT>", token="<TOKEN>", secret="<SECRET>")
#deploy_shinystan(sso, appName, account = NULL, ..., deploy = TRUE)

my_stanfit <- args[1]
# If you have a stanfit object then you can launch ShinyStan directly
my_sso <- launch_shinystan(my_stanfit)
launch_shinystan(my_stanfit)


#deploy_shinystan(sso, appName = "my-model", account = "username")

# If you only have one ShinyApps account configured then you can also omit
# the 'account' argument.

#deploy_shinystan(sso, appName = "my-model")
# }
