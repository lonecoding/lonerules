# 从最小链路到 v0.1

以下命令均在项目根目录、激活虚拟环境后运行。README 提供安装步骤。

## 1. 先确定输入规则

维护 `data/rules/` 中的六个 YAML 文件，使用统一类型和来源标识。
`data/sources.yaml` 记录作者、URL 和许可证。当前 20 条均为原创手工选择，
没有导入第三方规则，不代表服务全部域名。

```bash
python -m src.validate --strict
```

应看到 `Validated 6 categories, 20 unique rules`。
规则增加后数量会相应变化。重复、未知类型、空值或格式错误会让命令失败，
并报告文件位置；修改源数据后再运行。

## 2. 标准化和冲突处理

`src/normalize.py` 处理域名大小写、末尾根点和 CIDR 网络地址；
`src/validate.py` 在标准化后识别重复。同分类普通构建去重并警告，
严格校验拒绝重复；跨分类相同规则始终报错，需要人工决定归属。
不同类型、父子域名或重叠网段不会被自动合并。

## 3. 生成客户端产物

`src/targets/quantumultx.py` 负责格式映射；
`profiles/quantumultx/basic.conf.template` 负责基础配置结构。
客户端策略名由 adapter 添加，源规则中不写 Quantumult X 语法。

```bash
python -m src.build
```

应看到 `Built 10 files in dist/`。其中包括六份 `.list`、一份基础配置、
来源表、MIT 许可证和 SHA-256 清单。正式 `.list` 包含第三列策略名。

## 4. 运行质量检查

```bash
python -m ruff check .
python -m ruff format --check .
python -m unittest discover -s tests -v
python -m src.build --check
```

代码检查应通过，测试以 `OK` 结束，最后显示 `Verified 10 files in dist/`。
`--check` 不会覆盖文件；它负责发现手工改动、缺失或过时产物。

## 5. 提交源码和生成结果

`dist/` 虽然进入 Git，仍然只能由程序维护。这样 GitHub 原始文件链接
可直接用于订阅，PR 也能查看规则变化。修改流程为：编辑源文件 → 校验 →
构建 → 测试 → 提交源文件与生成结果。

```bash
git status --short
git add data src profiles tests dist
git commit -m "feat: extend AI rule coverage"
git push
```

命令中的路径和提交说明要按真实变更调整；文档或依赖变更也需要一并提交。
每次 push / PR 会自动运行 CI，不一致的生成文件会导致失败。

## 6. 发布版本

版本号、CHANGELOG 和发布说明准备好，main 分支 CI 全部通过后，再创建版本标签。
标签触发 CI；只有所有校验成功，发布任务才会上传产物。
具体命令和恢复说明见 `maintenance.md`。

## 7. 在设备上验证

从 Release 下载 `basic.conf` 并导入 Quantumult X，然后添加自己的节点。
默认直连；将 Proxy 策略从 direct 切到 proxy 才启用代理。
查看请求日志确认 AI、Apple 和 Global 等分类实际命中。

构建和自动化测试不等于 iPhone 实测。v0.1.0 发布说明明确记录设备导入和
实际分流尚未验证；设备检查项目见 `quantumultx.md`。
