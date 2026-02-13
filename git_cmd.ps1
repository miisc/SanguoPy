# 1. 初始化Git仓库
git init

# 2. 配置Git用户信息
git config user.name "Nico"
git config user.email "nico_6@sina.com"
git config init.defaultBranch main

# 3. 创建.gitignore文件
# Check if .gitignore already exists to avoid duplication
if (Test-Path ".gitignore") {
    Write-Host ".gitignore file already exists, skipping creation"
} else {
    # Define gitignore content as array for better maintainability
    $gitignoreContent = @(
        "# System generated files",
        ".DS_Store",
        "Thumbs.db",
        "",
        "# Editor and IDE generated files",
        ".vscode/",
        "*.swp",
        "*~",
        "",
        "# Log files",
        "*.log",
        "",
        "# Temporary files",
        "*.tmp",
        "*.temp",
        "",
        "# Game save files",
        "saves/",
        "*.save"
    )
    
    # Write all content at once for better performance
    $gitignoreContent -join "`n" | Out-File -FilePath ".gitignore" -Encoding UTF8
    Write-Host ".gitignore file created successfully"
}

# 4. 添加所有文件到暂存区
git add .

# 5. 进行初始提交
git commit -m "feat: Initialize Three Kingdoms Strategy Game Project

- Create basic project structure
- Add requirements document
- Set up Git version control"

# 6. 创建并切换到develop分支
git checkout -b develop
