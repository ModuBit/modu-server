# MODU Server

## 开发

### 包管理

- [Configure a conda virtual environment in PyCharm](https://www.jetbrains.com/help/pycharm/conda-support-creating-conda-virtual-environment.html)
- [Configure a Poetry environment in PyCharm](https://www.jetbrains.com/help/pycharm/poetry.html)

### 依赖
```shell
conda deactivate
conda env remove -n modu-server
conda create -n modu-server python=3.11
conda activate modu-server
pip install poetry
poetry install
```

### 组件
```shell
cd deploy/docker
docker-compose -f docker-compose-dev.yml -p modu-dev up
```