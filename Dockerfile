# 使用官方轻量级 Python 镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /J_class

# 拷贝项目所有文件到容器中
COPY . /J_class

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 启用环境变量（如 DB 配置）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 暴露 Flask 使用的端口
EXPOSE 5000

# 容器启动时运行 Flask 服务
CMD ["python", "Javelin.py"]
