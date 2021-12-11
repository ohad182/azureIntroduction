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

az webapp up --sku B1 --name $appName

az sql server create -n $sqlServerName -g $resource_group \
            -l $location -u $sqlServerUsername -p $sqlServerPassword

echo "Creating the database..."
az sql db create -g $resource_group -s $sqlServerName -n $sqlDatabaseName --service-objective Basic

az webapp show -n $appName -g $resource_group --query "outboundIpAddresses" -o tsv

echo "Configuring firewall..."
az sql server firewall-rule create -g $resource_group -s $sqlServerName -n AllowWebAppDemo --start-ip-address 192.168.1.0 --end-ip-address 192.168.1.255

connectionString="Server=tcp:$sqlServerName.database.windows.net;Database=$sqlDatabaseName;User ID=$sqlServerUsername@$sqlServerName;Password=$sqlServerPassword;Trusted_Connection=False;Encrypt=True;"
echo "$connectionString"

echo "Deploying bing"
az deployment group create --resource-group $resource_group --template-file bing-template/template.json --parameters '@bing-template/parameters.json'
#az deployment group create --resource-group web-app --template-file bing-template/template.json --parameters '@bing-template/parameters.json'