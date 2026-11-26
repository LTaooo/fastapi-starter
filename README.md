## 环境要求

- Python 3.12
- uv

## 快速开始

```shell
uv sync
uv run uvicorn main:app --reload
```

开发环境也可使用 `uv run fastapi dev main.py`；生产环境使用 `uv run fastapi run main.py`。

## API 文档

访问 `/docs` 使用 Scalar 文档，文档路径由 `docs.path` 配置。非生产环境直接开放；生产环境须同时配置有效的 `docs.username` 和 `docs.password`，此时 `/docs` 和 `/openapi.json` 启用 HTTP Basic 认证，未同时配置凭据则不注册文档路由。

## 开发

依赖统一由 uv 管理：

```shell
uv add <包名>        # 添加运行时依赖
uv add --dev <包名>  # 添加开发依赖
```

安装 pre-commit hook：

```shell
uv run pre-commit install
```

一次性执行的任务可通过 `core/script_runner.py` 的 `run_script` 在应用生命周期内运行，统一处理用户中断与未预期异常。

面向 AI 的运维命令统一从 `cli` 包进入：`uv run python -m cli <子命令>`，`uv run python -m cli --help` 列出全部子命令；结果以一行 JSON 打印到标准输出，日志与告警走标准错误。新增子命令时实现 `cli/contract/cli_command.py` 的 `CliCommand`，并登记到 `cli/registry.py`。

## 配置

应用从环境变量、`.env` 文件和 Nacos 加载配置。复制 `.env.example` 为 `.env` 后填写本机配置；`.env.example` 列出了全部配置项和默认值。应用级环境变量使用大写加下划线（如 `APP_PORT`），分组配置使用小写加点号（如 `mysql.host`、`crontab.enable`）。

## 依赖注入

`Container` 按构造函数的必填类型注解递归注入依赖，实例在当前进程内共享。由容器解析的类须带 `@injectable` 标记，未标记的类在解析时抛 `TypeError`；该约束只覆盖容器解析的类，基础设施代码直接 `Config.get()` 读取的配置类不受约束。配置类须继承 `pydantic_settings.BaseSettings`，被容器解析时同样需要标记，容器通过 `Config.get()` 加载环境变量、`.env` 或已取得的 Nacos 配置，不直接反射配置类的构造参数。

```python
from core.di.injectable import injectable


@injectable
class BookService:
    """由容器构造的服务。"""
```

端点通过 `inject(服务类型)` 声明依赖：

```python
from fastapi import APIRouter

from app.service.book_service import BookService
from core.di.dependency import inject

router = APIRouter()


@router.get('/book/count')
async def book_count(service: BookService = inject(BookService)) -> int:
    """返回可借阅书籍数量。"""
    return await service.count()
```

- 控制器使用 `inject(服务类型)` 声明依赖。服务在请求期间由异步依赖函数解析，应用的 lifespan 须先完成配置加载；端点不直接访问容器，不在模块导入时创建实例。
- 由容器解析的类必须带 `@injectable` 标记；未标记时解析抛 `TypeError`，消息指明类名与所属参数。标记可被继承，子类无需重复声明；由容器解析的配置类同样需要标记。
- `@injectable` 只声明「该类可由容器构造」，与参数规则正交：注入哪些参数仍由「无默认值的必填参数」决定。
- `get(类型)` 首次解析并缓存实例；`set(类型, 实例)` 显式注册或覆盖实例，优先于自动创建，注册的实例不受标记约束。
- 带默认值的参数保留默认值，不参与注入或注解求值；需要注入的依赖声明为必填参数。内建类型及数值、路径、日期时间、UUID、枚举等常见值类型须显式注册，必填联合类型不自动解析。
- 配置在首次解析时固定，修改配置后需重启进程。`Config.update_config()` 不替换容器中已缓存的配置或服务；`set()` 也不回写已构造对象持有的依赖。
- Nacos 变更监听尚未执行配置重载，不支持自动热更新。多 worker 各自拥有独立容器和任务状态。

## 定时任务

调度器随应用 lifespan 启动和关闭，任务清单在 `config/crontab_config.py` 的 `CrontabConfig.register_jobs` 中声明。定时任务时区由 `crontab.timezone` 配置，默认为 `Asia/Shanghai`；cron 触发器按该时区解释。

- 默认关闭，需显式配置 `crontab.enable=true`；配置在启动时读取，变更后需重启进程。
- 错过触发时刻的任务在短时间内仍会补执行一次，且只补一次；长时间阻塞则丢弃本次触发。
- 开启 `crontab.singleton` 时，正常情况下只有一个实例派发任务，其余实例空转等待，并在持锁实例退出后自动接手。
- 单例保证的是调度者唯一而非业务执行互斥：故障切换窗口内两个实例可能各派发一次任务，同一次业务执行的跨实例互斥由任务自身保证；持有者失效后，已在执行的任务会跑完，不会被中断。
- 实例正常停止时其他实例立即接手；崩溃或被强杀时会出现最长约 80 秒没有实例执行任务的空窗。
- Redis 未启用时锁不起作用，各实例都会执行任务，启动日志给出警告。

## 消息队列

队列通过 `core/rabbitmq/queue_interface.py` 的 `QueueInterface` 声明：子类实现 `queue` 与 `consume`，可选覆写 `is_enabled`、`ack_policy`、`channel`。所有队列类登记在 `config/queue_config.py` 的 `QueueConfig.queues` 中，由 lifespan 在启动 RabbitMQ 之前统一装配订阅。

## 升级说明

### RabbitMQ 持久化交换机

旧版本声明的交换机默认为非持久化（durable=False），当前版本使用持久化交换机（durable=True）。已启用 RabbitMQ 的环境从旧版本升级时，必须先删除旧交换机（名称默认 `exchange_<app_name>_<app_env>`），否则首次启动会返回 406 PRECONDITION_FAILED。删除交换机后，消费者启动时会重新声明交换机并重建绑定。

### 文档路由的生产环境开关

文档改由 `core/documentation.py` 注册：非生产环境始终注册 `/docs` 与 `/openapi.json`；生产环境只有同时配置 `docs.username` 和 `docs.password` 才注册并启用 Basic 认证，否则两者都不注册。旧版本用 `docs_url` 在非生产环境开放文档、生产环境彻底关闭，未提供认证。

### 移除 MCP 集成

`core/mcp_server/`、`config/mcp_config.py` 及 `main.py`、`core/lifespan.py`、`routes/routes.py` 中的 MCP 分支已移除，`.env` 中的 `mcp.enable` 不再生效。

### AppConfig 字段改名

`AppConfig` 的 `host`、`port`、`workers` 已改名为 `app_host`、`app_port`、`app_workers`，环境变量相应改为 `APP_HOST`、`APP_PORT`、`APP_WORKERS`；新增 `docs_path`、`docs_username`、`docs_password` 三项文档配置。

### 业务异常改名

`core/exception/runtime_exception.py` 的 `RuntimeException` 已移除，业务失败改抛 `core/exception/biz_exception.py` 的 `BizException`，其 `message` 由全局异常处理原样返回给调用方。
