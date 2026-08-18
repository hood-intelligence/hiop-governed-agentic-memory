# Deploy HIOP Governed Agentic Memory to AWS Lambda + Function URL.
# Region: us-east-2
# Requires: aws login, and CRDB_DSN set in THIS shell (never printed).
#   cd HIOP-COCKROACH-AWS-HACKATHON-RC1
#   $env:AWS_DEFAULT_REGION = "us-east-2"
#   .\scripts\06_deploy_lambda.ps1

$ErrorActionPreference = "Stop"
$Aws = "C:\Users\glitt\AppData\Local\Programs\Amazon\AWSCLIV2\aws.exe"
if (-not (Test-Path $Aws)) { $Aws = "aws" }

$Root = Split-Path $PSScriptRoot -Parent
$Zip = Join-Path $Root "dist\lambda-hiop-governed-memory.zip"
$Fn = "hiop-governed-agentic-memory"
$Region = "us-east-2"
if ($env:AWS_DEFAULT_REGION) { $Region = $env:AWS_DEFAULT_REGION }
$RoleName = "hiop-governed-memory-lambda-role"

if (-not (Test-Path $Zip)) {
  throw "Missing zip. Run scripts\03_build_lambda_zip.ps1 first."
}

Write-Host "Checking AWS identity..."
& $Aws sts get-caller-identity --region $Region | Out-Host

if (-not $env:CRDB_DSN -and $env:HIOP_CRDB_DSN) {
  $env:CRDB_DSN = $env:HIOP_CRDB_DSN
  Write-Host "Using HIOP_CRDB_DSN from this shell (value not printed)."
}
if (-not $env:CRDB_DSN) {
  Write-Host "Neither CRDB_DSN nor HIOP_CRDB_DSN is set in this shell."
  Write-Host "In THIS window, set it from your notes, then rerun. Example:"
  Write-Host '  $env:CRDB_DSN = "<your cockroach url>"'
  Write-Host "Do not paste the URL into Grok."
  throw "CRDB_DSN is not set in this shell."
}

$Mode = "cockroach"
Write-Host "HIOP_MEMORY_MODE=$Mode"

$trust = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
$roleArn = $null
try {
  $roleArn = (& $Aws iam get-role --role-name $RoleName --query Role.Arn --output text 2>$null)
} catch {
  $roleArn = $null
}
if (-not $roleArn) {
  Write-Host "Creating IAM role $RoleName"
  $roleArn = & $Aws iam create-role --role-name $RoleName --assume-role-policy-document $trust --query Role.Arn --output text
  & $Aws iam attach-role-policy --role-name $RoleName --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole | Out-Null
  Start-Sleep -Seconds 12
}
Write-Host "ROLE=$roleArn"

$exists = $false
try {
  & $Aws lambda get-function --function-name $Fn --region $Region | Out-Null
  $exists = $true
} catch {
  $exists = $false
}

if ($exists) {
  Write-Host "Updating function code..."
  & $Aws lambda update-function-code --function-name $Fn --zip-file "fileb://$Zip" --region $Region | Out-Null
  & $Aws lambda wait function-updated --function-name $Fn --region $Region
} else {
  Write-Host "Creating function..."
  & $Aws lambda create-function --function-name $Fn --runtime python3.12 --architectures x86_64 --handler handler.lambda_handler --role $roleArn --zip-file "fileb://$Zip" --timeout 60 --memory-size 512 --region $Region | Out-Null
  & $Aws lambda wait function-active --function-name $Fn --region $Region
}

# Do not interpolate DSN into Write-Host
$envJson = @{
  Variables = @{
    HIOP_MEMORY_MODE = "cockroach"
    HIOP_PRODUCTION_CERTIFIED = "false"
    CRDB_DSN = $env:CRDB_DSN
  }
} | ConvertTo-Json -Compress
$envFile = Join-Path $env:TEMP "hiop-lambda-env.json"
Set-Content -Path $envFile -Value $envJson -Encoding ascii

& $Aws lambda update-function-configuration --function-name $Fn --timeout 60 --memory-size 512 --environment "file://$envFile" --region $Region | Out-Null
Remove-Item $envFile -Force -ErrorAction SilentlyContinue
& $Aws lambda wait function-updated --function-name $Fn --region $Region
& $Aws lambda put-function-concurrency --function-name $Fn --reserved-concurrent-executions 1 --region $Region | Out-Null

# Authenticated invoke first
$payloadFile = Join-Path $env:TEMP "hiop-lambda-payload.json"
$invokeOut = Join-Path $env:TEMP "hiop-lambda-invoke.json"
Set-Content -Path $payloadFile -Value '{"goal":"lab safe"}' -Encoding ascii
Write-Host "Invoking function (authenticated)..."
& $Aws lambda invoke --function-name $Fn --region $Region --cli-binary-format raw-in-base64-out --payload "file://$payloadFile" $invokeOut | Out-Host
$invokeBody = Get-Content $invokeOut -Raw
if ($invokeBody -match "postgresql://|CRDB_DSN|password") {
  throw "Invoke output looked like it contained a secret. Stopping."
}
Write-Host "INVOKE_BODY_SANITIZED:"
Write-Host $invokeBody

$url = $null
try {
  $url = (& $Aws lambda get-function-url-config --function-name $Fn --region $Region --query FunctionUrl --output text 2>$null)
} catch {
  $url = $null
}
if (-not $url -or $url -eq "None") {
  Write-Host "Creating Function URL (Auth NONE, contest demo only)..."
  $url = & $Aws lambda create-function-url-config --function-name $Fn --auth-type NONE --cors "AllowOrigins=*,AllowMethods=*,AllowHeaders=*" --region $Region --query FunctionUrl --output text
  try {
    & $Aws lambda add-permission --function-name $Fn --statement-id FunctionURLAllowPublicAccess --action lambda:InvokeFunctionUrl --principal "*" --function-url-auth-type NONE --region $Region | Out-Null
  } catch { }
}

Write-Host "DEMO_URL=$url"
$arn = & $Aws lambda get-function --function-name $Fn --region $Region --query Configuration.FunctionArn --output text
Write-Host "ARN=$arn"
Write-Host "REGION=$Region"
Write-Host "After judging: aws lambda delete-function-url-config --function-name $Fn --region $Region"

$note = Join-Path $Root "docs\AWS-DEMO-URL.txt"
Set-Content -Path $note -Value "DEMO_URL=$url`nREGION=$Region`nFUNCTION=$Fn`nMODE=$Mode`nproduction_certified=false`n" -Encoding ascii
Write-Host "Wrote docs\AWS-DEMO-URL.txt"
