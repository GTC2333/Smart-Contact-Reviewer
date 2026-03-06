# 贡献指南

感谢您对项目的关注！本文档说明如何参与项目贡献。

## 贡献方式

### 1. 报告问题

- 使用 GitHub Issues
- 提供详细的问题描述
- 包含复现步骤

### 2. 提出功能建议

- 在 Issues 中讨论
- 说明使用场景
- 提供实现思路（可选）

### 3. 提交代码

- Fork 仓库
- 创建功能分支
- 提交 Pull Request

## 开发流程

### 1. Fork 和克隆

```bash
# Fork 仓库后
git clone https://github.com/your-username/smart_contract_audit.git
cd smart_contract_audit
```

### 2. 设置上游

```bash
git remote add upstream https://github.com/original-repo/smart_contract_audit.git
```

### 3. 创建分支

```bash
git checkout -b feature/your-feature
# 或
git checkout -b fix/your-fix
```

### 4. 开发

- 编写代码
- 添加测试
- 更新文档

### 5. 提交

```bash
git add .
git commit -m "feat: 添加新功能"
```

提交信息格式：
- `feat:` 新功能
- `fix:` 修复
- `docs:` 文档
- `style:` 格式
- `refactor:` 重构
- `test:` 测试
- `chore:` 其他

### 6. 推送和 PR

```bash
git push origin feature/your-feature
# 在 GitHub 创建 Pull Request
```

## 代码规范

### Python 代码

- 遵循 PEP 8
- 使用 Black 格式化
- 添加类型提示
- 编写文档字符串

### 测试

- 为新功能添加测试
- 确保测试通过
- 保持测试覆盖率

### 文档

- 更新相关文档
- 添加代码注释
- 更新示例

## Pull Request 检查清单

- [ ] 代码通过测试
- [ ] 代码格式化（Black）
- [ ] 通过 lint 检查
- [ ] 更新了文档
- [ ] 添加了测试
- [ ] 提交信息清晰

## 代码审查

- 保持开放心态
- 接受建设性反馈
- 及时响应评论
- 持续改进

## 行为准则

- 尊重他人
- 建设性讨论
- 包容不同观点
- 专业沟通

## 获取帮助

- 查看文档
- 搜索 Issues
- 创建新 Issue
- 联系维护者

感谢您的贡献！
