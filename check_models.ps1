# check_models.ps1
$catalog = Invoke-RestMethod -Uri https://openrouter.ai/api/v1/models
$currentIds = $catalog.data.id
$myModels = @(
    "deepseek/deepseek-v4-pro",
    "google/gemini-2.5-flash",
    "moonshotai/kimi-k2.5",
    "inclusionai/ring-2.6-1t",
    "deepseek/deepseek-v4-flash",
    "deepseek/deepseek-chat",
    "perceptron/perceptron-mk1"
)
$missing = $myModels | Where-Object { $_ -notin $currentIds }
if ($missing) {
    Write-Host "⚠️  MISSING MODELS:" -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  - $_" }
} else {
    Write-Host "✅ All models still available" -ForegroundColor Green
}
