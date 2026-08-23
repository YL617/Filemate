# npm audit 高危依赖评估

> 评估日期：2026-08-24
> 命令：`npm audit --json`、`npm audit fix --dry-run`
> 结论：1 个 high severity 间接依赖，修复可用且为低风险补丁升级。

## 漏洞详情

| 项 | 值 |
|---|---|
| 依赖 | `nanoid` |
| 版本 | `<3.3.18`，当前 3.3.16 |
| 严重度 | high |
| 类型 | 自定义生成器在 size 为 0 时可能无限循环 |
| 影响 | 潜在 DoS，非直接依赖 |
| 是否直接依赖 | 否 |

## 修复方案

`npm audit fix --dry-run` 显示：

```text
change nanoid 3.3.16 => 3.3.18
changed 1 package
```

建议：

1. 优先执行 `npm audit fix`，将 `nanoid` 升到 3.3.18。
2. 升级后运行 `npm ci && npm run build` 确认前端构建无回归。
3. 若团队决定暂不升级，需在 Issue 中记录“接受风险”及理由。

## 决策

是否升级由杨乐与张金宝确认后执行；本评估不代为决策。
