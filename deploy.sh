resource_group="web-app"
location="westeurope"
appName="ohadc-app"
planName="ohadc-web-app-service-plan"
sqlServerName="web-app-sql-srv-ohadc"
sqlDatabaseName="web-app-sql-db-ohadc"
sqlServerUsername="db_admin"
sqlServerPassword="db_Password!"
git_repo="https://github.com/ohad182/azureIntroduction"
branch="web-app"


echo "Deleting resource group $resource_group..."
az group delete -n $resource_group --yes

echo "Creating resource group $resource_group..."
az group create -n $resource_group -l $location

# create the app service plan
# allowed sku values B1, B2, B3, D1, F1, FREE, P1, P1V2, P2, P2V2, P3, P3V2, S1, S2, S3, SHARED.
echo "Creating service plan  $planName..."
az appservice plan create -n $planName -g $resource_group -l $location --sku B1

echo "Creating the web app..."
az webapp create -n $appName -g $resource_group --plan $planName

az webapp deployment source config -n $appName -g $resource_group \
    --repo-url $git_repo --branch $branch --manual-integration

az sql server create -n $sqlServerName -g $resource_group \
            -l $location -u $sqlServerUsername -p $sqlServerPassword

echo "Creating the database..."
az sql db create -g $resource_group -s $sqlServerName -n $sqlDatabaseName --service-objective Basic

az webapp show -n $appName -g $resource_group --query "outboundIpAddresses" -o tsv

echo "Configuring firewall..."
az sql server firewall-rule create -g $resource_group -s $sqlServerName -n AllowWebAppDemo --start-ip-address 192.168.1.0 --end-ip-address 192.168.1.255

connectionString="Server=tcp:$sqlServerName.database.windows.net;Database=$sqlDatabaseName;User ID=$sqlServerUsername@$sqlServerName;Password=$sqlServerPassword;Trusted_Connection=False;Encrypt=True;"
echo "$connectionString"