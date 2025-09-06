# 使用官方 Python 运行时作为基础镜像
FROM docker.xuanyuan.me/python:3.12-slim

# 设置时区
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 设置工作目录
WORKDIR /app

# 将 requirements.txt 复制到容器中
COPY requirements.txt .

# 安装项目依赖
RUN pip install --no-cache-dir -r requirements.txt

# 将应用代码复制到容器中
COPY . .

# 运行应用
CMD ["python3", "stream_server.py"]