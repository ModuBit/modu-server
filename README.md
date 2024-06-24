# CubeChat Server

## 开发

### 包管理

- [Configure a conda virtual environment in PyCharm](https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html)
- [Configure a Poetry environment in PyCharm](https://www.jetbrains.com/help/pycharm/poetry.html)

### 依赖
```shell
conda deactivate
conda env remove -n cube-chat-server
conda create -n cube-chat-server python=3.11
conda activate cube-chat-server
pip install poetry
poetry install
```

### 组件
```shell
cd deploy/docker
docker-compose -f docker-compose-dev.yml -p cube-chat-dev up
```