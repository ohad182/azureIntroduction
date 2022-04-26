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
sql_driver="Driver={ODBC Driver 17 for SQL Server}"


echo "Deleting resource group $resource_group..."
az group delete -n $resource_group --yes

echo "Creating resource group $resource_group..."
az group create -n $resource_group -l $location

echo "Configuring resource group $resource_group to be default..."
az configure --defaults group=$resource_group

echo "Creating the sql server..."
az sql server create -n $sqlServerName -g $resource_group \
            -l $location -u $sqlServerUsername -p $sqlServerPassword

echo "Creating the database..."
az sql db create -g $resource_group -s $sqlServerName -n $sqlDatabaseName --service-objective Basic

echo "Writing connection string"
connectionString="$sql_driver;Server=tcp:$sqlServerName.database.windows.net,1433;Database=$sqlDatabaseName;Uid=$sqlServerUsername;Pwd=$sqlServerPassword;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
echo "$connectionString"
echo "$connectionString" > connection_string.txt

echo "Configure sql access for internal azure datacenter"
az sql server firewall-rule create -g $resource_group -s $sqlServerName -n AllowWebAppAzure1 --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

echo "Configuring firewall..."
az sql server firewall-rule create -g $resource_group -s $sqlServerName -n AllowWebAppDemo --start-ip-address 192.168.1.0 --end-ip-address 192.168.1.255

echo "Creating the web app..."
az webapp up --sku B1 --name $appName

#az webapp show -n $appName -g $resource_group --query "outboundIpAddresses" -o tsv

#echo "Deploying bing"
#az deployment group create --resource-group $resource_group --template-file bing-template/template.json --parameters '@bing-template/parameters.json'
###az deployment group create --resource-group bing-rg --template-file bing-template/template.json --parameters '@bing-template/parameters.json'