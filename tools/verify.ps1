# tools/verify.ps1 — SanguoPy 自动化验证脚本
# 用法：powershell -ExecutionPolicy Bypass -File tools/verify.ps1
# 成功：全部测试绿（exit 0）；失败：打印摘要（exit 1）

param(
    [int]$MinCoverage = 85,
    [switch]$SkipCoverage
)

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
$pytest  = Join-Path $root ".venv\Scripts\pytest.exe"

if (-not (Test-Path $pytest)) {
    Write-Host "[ERROR] pytest 未找到，请先运行: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ pytest pytest-mock pytest-cov" -ForegroundColor Red
    exit 1
}

$failed = 0

function Run-Suite {
    param([string]$label, [string]$path)
    Write-Host "`n=== $label ===" -ForegroundColor Cyan
    & $pytest $path -v --tb=short --no-header -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] $label" -ForegroundColor Red
        $script:failed++
    } else {
        Write-Host "[PASS] $label" -ForegroundColor Green
    }
}

Push-Location $root
try {
    Run-Suite "Unit: GameModel"             "src/test/unit/test_game_model.py"
    Run-Suite "Unit: CourtMeeting"          "src/test/unit/test_court_meeting.py"
    Run-Suite "Unit: LLMIntegration"        "src/test/unit/test_llm_integration.py"
    Run-Suite "Unit: LlmValidationGateway"  "src/test/unit/test_llm_validation_gateway.py"
    Run-Suite "Unit: MvpRuleContracts"      "src/test/unit/test_mvp_rule_contracts.py"
    Run-Suite "Unit: TempCommandPolicy"     "src/test/unit/test_temp_command_policy.py"
    Run-Suite "Integration: CourtFlow"      "src/test/integration/test_court_flow.py"

    if (-not $SkipCoverage) {
        Write-Host "`n=== Coverage (fail-under: $MinCoverage%) ===" -ForegroundColor Cyan
        & $pytest src/test/unit src/test/integration -q --no-header --tb=short --cov=src/game --cov-report=term-missing --cov-fail-under=$MinCoverage
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[FAIL] Coverage" -ForegroundColor Red
            $script:failed++
        } else {
            Write-Host "[PASS] Coverage" -ForegroundColor Green
        }
    }
} finally {
    Pop-Location
}

if ($failed -gt 0) {
    Write-Host "`n[RESULT] $failed suite(s) FAILED" -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n[RESULT] All suites PASSED" -ForegroundColor Green
    exit 0
}
