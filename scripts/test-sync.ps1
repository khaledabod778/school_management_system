param(
    [string]$ApiUrl = "https://your-api-domain.com",
    [string]$ApiKey = "..."
)

$headers = @{ "X-API-Key" = $ApiKey }

$body = @{
    instance_id = "test-device"
    device_id   = "test-001"
    operations  = @(
        @{
            idempotency_key = "test-op-001"
            entity_type     = "grades"
            entity_uuid     = "test-uuid-001"
            operation_type  = "INSERT"
            payload = @{
                grade_name   = "الصف الأول"
                stage_name   = "الابتدائي"
                max_capacity = 30
                sync_uuid    = "test-uuid-001"
                sync_version = 1
            }
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/api/sync/push" `
        -Method Post -Headers $headers -Body $body `
        -ContentType "application/json; charset=utf-8"
    Write-Host "✅ نجح الطلب:" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 10
} catch {
    Write-Host "❌ فشل الطلب:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    if ($_.ErrorDetails) { Write-Host $_.ErrorDetails.Message }
}