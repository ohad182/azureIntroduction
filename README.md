# azureIntroduction

Depoy:
gitrepo="https://github.com/ohad182/azureIntroduction"
branch="web-app"
appName="ohadc-app"
resourceGroup="web-app"

az webapp deployment source config -n $appName -g $resourceGroup --repo-url $gitrepo --branch $branch --manual-integration

after first deployment:
az webapp deployment source sync -n $appName -g $resourceGroup