# Git命令参考

## 基本命令

### 初始化与配置

```bash
# 初始化仓库
git init

# 克隆仓库
git clone <url>

# 配置用户信息
git config --global user.name "用户名"
git config --global user.email "邮箱"

# 查看配置
git config --list
```

### 基本操作

```bash
# 查看仓库状态
git status

# 添加文件到暂存区
git add <文件名>
git add .  # 添加所有文件

# 提交更改
git commit -m "提交信息"

# 查看提交历史
git log
git log --oneline  # 简洁显示
git log --graph --oneline --decorate  # 图形化显示

# 查看文件差异
git diff  # 工作区与暂存区差异
git diff --cached  # 暂存区与最新提交差异
git diff HEAD  # 工作区与最新提交差异
```

## 分支操作

### 查看与创建

```bash
# 查看所有分支
git branch
git branch -a  # 查看所有分支（包括远程）

# 创建分支
git branch <分支名>

# 切换分支
git checkout <分支名>

# 创建并切换分支
git checkout -b <分支名>
```

### 合并与删除

```bash
# 合并分支
git merge <分支名>

# 删除分支
git branch -d <分支名>  # 已合并分支
git branch -D <分支名>  # 强制删除

# 重命名分支
git branch -m <旧名> <新名>
```

## 远程操作

```bash
# 查看远程仓库
git remote -v

# 添加远程仓库
git remote add <名称> <url>

# 推送到远程仓库
git push <远程名> <分支名>
git push -u origin main  # 首次推送并设置上游

# 从远程仓库拉取
git pull <远程名> <分支名>
git fetch  # 获取但不合并
```

## 撤销操作

### 文件级撤销

```bash
# 撤销工作区修改
git checkout -- <文件名>

# 撤销暂存区修改
git reset HEAD <文件名>

# 恢复删除的文件
git checkout HEAD -- <文件名>
```

### 提交级撤销

```bash
# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1

# 修改最后一次提交
git commit --amend
```

### 高级撤销

```bash
# 回滚到指定提交（保留修改）
git reset --soft <提交哈希>

# 回滚到指定提交（丢弃修改）
git reset --hard <提交哈希>

# 逆向提交（创建新提交撤销旧提交）
git revert <提交哈希>
```

## 标签操作

```bash
# 创建标签
git tag <标签名>
git tag -a <标签名> -m "标签信息"

# 查看标签
git tag
git show <标签名>

# 推送标签
git push origin <标签名>
git push --tags  # 推送所有标签

# 删除标签
git tag -d <标签名>
git push origin :refs/tags/<标签名>  # 删除远程标签
```

## 暂存操作

```bash
# 暂存当前工作
git stash

# 查看暂存列表
git stash list

# 恢复暂存
git stash pop  # 恢复并删除
git stash apply  # 恢复但不删除

# 删除暂存
git stash drop

# 清空所有暂存
git stash clear
```

## 查找与搜索

```bash
# 查找包含特定内容的提交
git log -S "内容"

# 查找修改特定文件的提交
git log -- <文件名>

# 查找特定作者的提交
git log --author="作者名"

# 搜索提交信息
git log --grep="关键词"
```

## 实用技巧

### 查看特定提交的修改

```bash
# 查看特定提交的详细修改
git show <提交哈希>

# 查看特定提交中特定文件的修改
git show <提交哈希>:<文件名>
```

### 比较分支

```bash
# 查看分支差异
git diff <分支1> <分支2>

# 查看分支间独有的提交
git log <分支1>..<分支2>
```

### 清理仓库

```bash
# 清理未跟踪的文件
git clean -f

# 清理未跟踪的文件和目录
git clean -fd

# 压缩仓库历史
git gc --prune=now
```

### 别名设置

```bash
# 设置别名
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.graph 'log --oneline --graph --decorate --all'
git config --global alias.amend 'commit --amend'
git config --global alias.undocommit 'reset --soft HEAD~1'
git config --global alias.filelog 'log -u'
```

## 常见问题解决

### 合并冲突

```bash
# 查看冲突文件
git status

# 手动编辑冲突文件后添加
git add <冲突文件>

# 继续合并
git commit
```

### 撤销合并

```bash
# 撤销最近一次合并（保留历史）
git revert -m 1 HEAD

# 撤销合并（不保留历史）
git reset --hard HEAD~1
```

### 修改提交历史

```bash
# 交互式变基（修改多个提交）
git rebase -i HEAD~n  # n为要修改的提交数

# 变基到指定提交
git rebase -i <提交哈希>
```

## 工作流程示例

### 功能开发流程

```bash
# 1. 切换到develop分支
git checkout develop

# 2. 创建功能分支
git checkout -b feature/new-feature

# 3. 开发并提交
git add .
git commit -m "feat: 实现新功能"

# 4. 切换回develop分支
git checkout develop

# 5. 合并功能分支
git merge --no-ff feature/new-feature

# 6. 删除功能分支
git branch -d feature/new-feature
```

### 发布流程

```bash
# 1. 合并develop到main
git checkout main
git merge --no-ff develop

# 2. 创建标签
git tag -a v1.0.0 -m "发布版本 1.0.0"

# 3. 推送
git push origin main
git push origin v1.0.0
```

通过掌握这些Git命令，您可以高效地管理项目版本控制，跟踪代码变更，并与团队成员协作开发。