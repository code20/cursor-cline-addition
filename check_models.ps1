# check_models.ps1
$catalog = Invoke-RestMethod -Uri https://openrouter.ai/api/v1/models
$currentIds = $catalog.data.id
$myModels = @(
    "moonshotai/kimi-k2.5",
    "deepseek/deepseek-v4-pro",
    "google/gemini-2.5-flash",
    "inclusionai/ring-2.6-1t",
    "perceptron/perceptron-mk1"
)
$missing = $myModels | Where-Object { $_ -notin $currentIds }
if ($missing) {
    Write-Host "⚠️  MISSING MODELS:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  - $_" }
} else {
    Write-Host "✅ All models still available" -ForegroundColor Green
}
