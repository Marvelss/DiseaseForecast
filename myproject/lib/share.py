import os

# 项目基础路径
PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 项目资源路径
RESOURCE_PATH = os.path.join(PROJECT_PATH, 'resource')
# 项目界面路径
PAGES_PATH = os.path.join(PROJECT_PATH, 'pages')
# 数据模板文件
RESOURCE_TEMPLATE_PATH = os.path.join(RESOURCE_PATH, 'template')
# 过程中处理的文件
RESOURCE_PROCESS_PATH = os.path.join(RESOURCE_PATH, 'process')
# 图片或图标文件
RESOURCE_IMAGES_PATH = os.path.join(RESOURCE_PATH, 'images')

# 配置文件路径
# CONFIG_PATH = os.path.join(BASE_DIR, "conf", "db_config.ini")
# 日志路径
# LOG_PATH = os.path.join(BASE_DIR, "conf", "log")
# 日值配置
# logger = myproject.lib.utils.setup_logging(
# os.path.join(LOG_PATH, myproject.lib.utils.log_date_name()))
