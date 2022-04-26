#!/bin/bash 

location="westeurope"
resource_group="azcli-resource-group"

# database variables
server="sql-srv-azcli"
database="sql-db-azcli"
login="db_admin"
password="db_Password!"
# startIP=10.5.45.0
# endIP=10.5.45.255
startIP=192.168.1.0
endIP=192.168.1.255

# add if exist delete
echo "Deleting resource group $resource_group..."
az group delete -n $resource_group --yes

echo "Creating resource group $resource_group..."
az group create --name $resource_group --location "$location"

echo "Creating $server in $location..."
az sql server create --name $server --resource-group $resource_group --location "$location" --admin-user $login --admin-password $password

echo "Configuring firewall..."
az sql server firewall-rule create --resource-group $resource_group --server $server -n AllowYourIp --start-ip-address $startIP --end-ip-address $endIP

echo "Creating $database on $server..."
az sql db create --resource-group $resource_group --server $server --name $database --edition GeneralPurpose --family Gen5 --capacity 2 

echo "Creating storage account..."
az storage account create --name azcli-ohadc-storage --resource-group $resource_group --location "$location" --sku Standard_ZRS --encryption-services blob

# create deployment 
echo "Deploying..."
az deployment group create --name machines-deployment --resource-group azcli-resource-group --template-file machines-score-template.json
