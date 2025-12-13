

import sys
import os
import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO, encoding='utf-8')
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Query, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from api.realtime.websocket_manager import manager
from api.file_handler.file_handler import file_handler

from core.node_registry import get_all_nodes, load_custom_nodes, _node_registry
from core.video_processing_nodes import *  
from core.wan22_nodes import *
from core.hunyuan_video_nodes import *
from core.stable_diffusion_nodes import *

# 导入模块管理器和插件管理器
from core.module.module_manager import module_manager
from core.module.module_registrar import register_module
from core.module.plugin_manager import plugin_manager

# 导入核心模块，确保它们被注册
import core.modules.workflow
import core.modules.task_queue

# 异步初始化模块系统
async def initialize_modules():
    try:
        # 注册并激活核心模块
        await module_manager.activate_module('workflow')
        await module_manager.activate_module('task_queue')
        
        # 初始化插件系统
        plugin_dir = os.path.join(os.path.dirname(__file__), '../../plugins')
        if not os.path.exists(plugin_dir):
            os.makedirs(plugin_dir)
        plugin_manager.add_plugin_dir(plugin_dir)
        
        # 发现并加载插件
        discovered_plugins = await plugin_manager.discover_plugins()
        for plugin_id in discovered_plugins:
            await plugin_manager.activate_module(plugin_id)
        
        logger.info('All core modules activated successfully')
        logger.info(f'Discovered {len(discovered_plugins)} plugins')
    except Exception as e:
        logger.error(f'Failed to initialize modules: {e}')

import importlib

# 模块API缓存
workflow_module_api = None
node_manager_api = None

# 定义应用生命周期管理
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global workflow_module_api, node_manager_api
    
    # 初始化模块系统
    await initialize_modules()
    
    # 获取工作流模块API
    workflow_module_api = module_manager.get_module_api('workflow')
    
    # 获取节点管理器插件API
    node_manager_api = module_manager.get_module_api('node_manager')
    
    # 获取并缓存插件索引
    from core.module.plugin_manager import plugin_manager
    await plugin_manager.fetch_and_cache_index()
    
    yield
    
    # 清理资源
    await module_manager.deactivate_module('workflow')
    if module_manager.get_module_state('node_manager') == 'activated':
        await module_manager.deactivate_module('node_manager')
    logger.info('Application shutdown complete')

app = FastAPI(
    title="Cognot AI API",
    description="AI 工作流引擎 API 接口，专注于 AI 绘图和 AI 视频处理",
    version="0.1.0",
    lifespan=lifespan
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# 配置静态文件服务
frontend_path = os.path.join(os.path.dirname(__file__), '../../frontend/dist')
# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Cognot AI API is running"}

# 模型管理接口
@app.get("/models")
async def get_available_models(model_type: str = None):
    """获取可用模型列表"""
    from core.ai_model_manager import ai_model_manager
    
    if model_type:
        models = ai_model_manager.get_available_models(model_type)
    else:
        models = []
        # 获取所有类型的模型
        for model_type in ai_model_manager.model_paths.keys():
            models.extend(ai_model_manager.get_available_models(model_type))
    
    # 格式化返回结果
    formatted_models = []
    for model_path in models:
        model_info = ai_model_manager.get_model_info(model_path)
        formatted_models.append(model_info)
    
    return {"models": formatted_models}

@app.get("/models/types")
async def get_model_types():
    """获取可用模型类型"""
    from core.ai_model_manager import ai_model_manager
    return {"model_types": ['all'] + ai_model_manager.get_user_friendly_model_types()}

@app.post("/models/upload")
async def upload_model(model_type: str, file: UploadFile = File(...)):
    """上传模型"""
    from core.ai_model_manager import ai_model_manager
    
    try:
        # 读取文件内容
        content = await file.read()
        
        # 上传模型
        success = ai_model_manager.upload_model(model_type, content, file.filename)
        
        if success:
            return {"status": "ok", "message": f"Model uploaded successfully: {file.filename}"}
        else:
            return {"status": "error", "message": "Failed to upload model"}
    except Exception as e:
        return {"status": "error", "message": f"Upload failed: {str(e)}"}

@app.delete("/models/delete")
async def delete_model(model_path: str = Query(...)):
    """删除模型"""
    from core.ai_model_manager import ai_model_manager
    
    try:
        success = ai_model_manager.delete_model(model_path)
        
        if success:
            return {"status": "ok", "message": f"Model deleted successfully: {model_path}"}
        else:
            return {"status": "error", "message": "Failed to delete model"}
    except Exception as e:
        return {"status": "error", "message": f"Delete failed: {str(e)}"}

nodes_metadata_cache = None

@app.get("/nodes")
async def get_nodes(load_sd: bool = False, load_third_party_ai: bool = False):
    
    global nodes_metadata_cache
    
    if load_sd:
        try:
            importlib.import_module('core.stable_diffusion_nodes')
            nodes_metadata_cache = None
        except ImportError:
            pass
    
    if load_third_party_ai:
        try:
            # 通过插件系统加载第三方AI节点
            from core.plugin_manager import plugin_manager
            node_manager_api = plugin_manager.get_module_api('node_manager')
            if node_manager_api:
                node_manager_api.load_third_party_ai_nodes()
                nodes_metadata_cache = None
            else:
                print("Failed to load third-party AI nodes: Node manager plugin not activated")
        except Exception as e:
            print(f"Failed to load third-party AI nodes: {e}")
    
    if nodes_metadata_cache is not None:
        return nodes_metadata_cache
    
    # 通过插件系统获取所有节点
    try:
        from core.plugin_manager import plugin_manager
        node_manager_api = plugin_manager.get_module_api('node_manager')
        if node_manager_api:
            nodes_metadata = node_manager_api.get_all_nodes()
            nodes_metadata_cache = nodes_metadata
            return nodes_metadata
        else:
            print("Warning: Node manager plugin not activated, returning empty nodes list")
            return []
    except Exception as e:
        print(f"Failed to get nodes from plugin system: {e}")
        return []

@app.post("/nodes/load")
async def load_nodes(module_path: str):
    
    try:
        # 通过插件系统加载自定义节点
        from core.plugin_manager import plugin_manager
        node_manager_api = plugin_manager.get_module_api('node_manager')
        if node_manager_api:
            node_manager_api.load_custom_nodes(module_path)
            return {"status": "ok", "message": f"Successfully loaded nodes from {module_path}"}
        else:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

workflow_executions = {}

workflows = []

class WorkflowDefinition(BaseModel):
    
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class WorkflowValidationResult(BaseModel):
    
    valid: bool
    missing_nodes: List[str]
    message: str

class ExecutionResponse(BaseModel):
    
    execution_id: str
    status: str
    message: str

class ExecutionStatus(BaseModel):
    
    execution_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/workflows/validate", response_model=WorkflowValidationResult)
async def validate_workflow(workflow_def: WorkflowDefinition):
    """
    验证工作流中使用的节点是否都已安装
    """
    try:
        workflow_data = workflow_def.dict()
        
        # 使用节点注册表验证工作流
        from core.node_registry import _node_registry
        missing_nodes = _node_registry.validate_workflow(workflow_data)
        
        if missing_nodes:
            return {
                "valid": False,
                "missing_nodes": missing_nodes,
                "message": f"Workflow contains {len(missing_nodes)} missing node(s)"
            }
        else:
            return {
                "valid": True,
                "missing_nodes": [],
                "message": "All nodes in workflow are installed"
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/api/nodes/metadata")
async def get_nodes_metadata():
    """
    获取所有已注册节点的元数据
    """
    from core.node_registry import _node_registry
    return _node_registry.get_all_nodes()

@app.post("/api/workflow/validate")
async def validate_workflow_api(workflow: Dict[str, Any]):
    """
    验证工作流中使用的节点是否都已安装
    
    Args:
        workflow: 工作流JSON数据
        
    Returns:
        JSON响应，包含验证结果和缺失的节点列表
    """
    from core.node_registry import _node_registry
    from core.module.plugin_manager import plugin_manager
    
    # 验证节点
    missing_nodes = _node_registry.validate_workflow(workflow)
    
    # 查找缺失节点对应的插件
    missing_nodes_plugins = plugin_manager.get_missing_nodes_plugins(missing_nodes)
    
    return {
        "is_valid": len(missing_nodes) == 0,
        "missing_nodes": missing_nodes,
        "missing_nodes_plugins": missing_nodes_plugins
    }

@app.post("/api/plugins/install_missing_nodes")
async def install_missing_nodes(request: Request):
    """
    一键安装缺失节点对应的插件
    
    Args:
        request: 包含工作流数据的请求体
        
    Returns:
        JSON响应，包含安装结果
    """
    from core.node_registry import _node_registry
    from core.module.plugin_manager import plugin_manager
    
    try:
        # 获取工作流数据
        workflow = await request.json()
        
        # 验证节点
        missing_nodes = _node_registry.validate_workflow(workflow)
        if not missing_nodes:
            return {"status": "success", "message": "No missing nodes found"}
        
        # 查找缺失节点对应的插件
        missing_nodes_plugins = plugin_manager.get_missing_nodes_plugins(missing_nodes)
        if not missing_nodes_plugins:
            return {"status": "error", "message": "No plugins found for missing nodes"}
        
        # 安装所有缺失的插件
        results = []
        for node_type, git_url in missing_nodes_plugins.items():
            success, error_msg = await plugin_manager.install_plugin(git_url)
            results.append({
                "node_type": node_type,
                "git_url": git_url,
                "success": success,
                "message": "Plugin installed successfully" if success else error_msg
            })
        
        # 检查是否需要重启
        restart_required = plugin_manager.restart_required()
        
        return {
            "status": "success",
            "message": f"Installed {len([r for r in results if r['success']])} out of {len(results)} plugins",
            "results": results,
            "restart_required": restart_required
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing missing nodes plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/plugins/list_available")
async def list_available_plugins():
    """
    获取所有已知且可安装的外部插件列表
    """
    from core.module.plugin_manager import plugin_manager
    plugins_dict = plugin_manager.get_available_plugins()
    # 将字典转换为数组格式，前端期望数组
    return list(plugins_dict.values())

class PluginInstallRequest(BaseModel):
    git_url: str

@app.post("/api/plugins/install")
async def install_plugin(request: PluginInstallRequest):
    """
    安装插件
    
    Args:
        request: 包含git_url的请求体
        
    Returns:
        安装结果
    """
    from core.module.plugin_manager import plugin_manager
    success, error_msg = await plugin_manager.install_plugin(request.git_url)
    
    if success:
        return {
            "status": "success",
            "message": f"Plugin installed successfully from {request.git_url}"
        }
    else:
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/plugins/find_by_node")
async def find_plugin_by_node_id(node_id: str = Query(...)):
    """
    根据节点ID查找对应的插件
    
    Args:
        node_id: 节点ID
        
    Returns:
        插件的Git URL，如果找不到则返回404
    """
    from core.module.plugin_manager import plugin_manager
    
    # 确保索引已加载
    if not await plugin_manager.ensure_index_loaded():
        raise HTTPException(status_code=500, detail="Failed to load plugin index")
    
    # 根据节点ID查找插件
    git_url = plugin_manager.find_plugin_by_node_id(node_id)
    
    if git_url:
        return {
            "status": "success",
            "git_url": git_url
        }
    else:
        raise HTTPException(status_code=404, detail=f"No plugin found for node ID: {node_id}")

# 自定义仓库管理接口
@app.get("/api/plugins/custom_repositories")
def get_custom_repositories():
    """
    获取用户自定义的仓库地址列表
    """
    from core.module.plugin_manager import plugin_manager
    
    return {
        "custom_repositories": plugin_manager.get_custom_repositories(),
        "disabled_repositories": plugin_manager.get_disabled_repositories()
    }

@app.post("/api/plugins/custom_repositories")
async def add_custom_repository(request: Request):
    """
    添加自定义仓库地址
    
    Returns:
        添加成功返回status: ok，失败返回status: error
    """
    from core.module.plugin_manager import plugin_manager
    
    try:
        data = await request.json()
        repo_url = data.get("repo_url")
        if not repo_url:
            raise HTTPException(status_code=400, detail="repo_url is required")
        
        if plugin_manager.add_custom_repository(repo_url):
            return {"status": "ok", "message": f"Repository added successfully: {repo_url}"}
        else:
            return {"status": "error", "message": f"Failed to add repository: {repo_url}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding custom repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/plugins/custom_repositories")
async def remove_custom_repository(request: Request):
    """
    删除自定义仓库地址
    
    Returns:
        删除成功返回status: ok，失败返回status: error
    """
    from core.module.plugin_manager import plugin_manager
    
    try:
        data = await request.json()
        repo_url = data.get("repo_url")
        if not repo_url:
            raise HTTPException(status_code=400, detail="repo_url is required")
        
        if plugin_manager.remove_custom_repository(repo_url):
            return {"status": "ok", "message": f"Repository removed successfully: {repo_url}"}
        else:
            return {"status": "error", "message": f"Failed to remove repository: {repo_url}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing custom repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/disable_repository")
async def disable_repository(request: Request):
    """
    禁用指定的仓库地址
    
    Returns:
        禁用成功返回status: ok，失败返回status: error
    """
    from core.module.plugin_manager import plugin_manager
    
    try:
        data = await request.json()
        repo_url = data.get("repo_url")
        if not repo_url:
            raise HTTPException(status_code=400, detail="repo_url is required")
        
        if plugin_manager.disable_repository(repo_url):
            return {"status": "ok", "message": f"Repository disabled successfully: {repo_url}"}
        else:
            return {"status": "error", "message": f"Failed to disable repository: {repo_url}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/enable_repository")
async def enable_repository(request: Request):
    """
    启用指定的仓库地址
    
    Returns:
        启用成功返回status: ok，失败返回status: error
    """
    from core.module.plugin_manager import plugin_manager
    
    try:
        data = await request.json()
        repo_url = data.get("repo_url")
        if not repo_url:
            raise HTTPException(status_code=400, detail="repo_url is required")
        
        if plugin_manager.enable_repository(repo_url):
            return {"status": "ok", "message": f"Repository enabled successfully: {repo_url}"}
        else:
            return {"status": "error", "message": f"Failed to enable repository: {repo_url}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/restart_required")
async def check_restart_required():
    """
    检查是否需要重启服务
    
    Returns:
        是否需要重启服务
    """
    from core.module.plugin_manager import plugin_manager
    restart_required = plugin_manager.restart_required()
    
    return {
        "restart_required": restart_required
    }

@app.post("/workflows/execute", response_model=ExecutionResponse)
async def submit_workflow(
    workflow_def: WorkflowDefinition,
):
    # 处理工作流执行请求
    # 使用任务队列模块API将工作流推送到后台执行
    
    workflow_data = workflow_def.dict()
    
    # 获取任务队列模块API
    task_queue_module_api = module_manager.get_module_api('task_queue')
    if not task_queue_module_api:
        raise HTTPException(status_code=503, detail="Task queue module not available")
    
    execution_id = await task_queue_module_api.enqueue_workflow(workflow_data)
    
    workflow_executions[execution_id] = {
        "status": "pending",
        "results": None,
        "error": None
    }
    
    return {
        "execution_id": execution_id,
        "status": "pending",
        "message": "Workflow execution submitted to queue"
    }

@app.get("/workflows/execution/{execution_id}", response_model=ExecutionStatus)
async def get_execution_status(execution_id: str):
    
    try:
        # 从任务队列模块API获取任务状态
        task_queue_module_api = module_manager.get_module_api('task_queue')
        if not task_queue_module_api:
            raise HTTPException(status_code=503, detail="Task queue module not available")
        
        job_status = task_queue_module_api.get_job_status(execution_id)
        
        # 更新本地执行状态缓存
        if execution_id in workflow_executions:
            workflow_executions[execution_id]["status"] = job_status["status"]
            workflow_executions[execution_id]["results"] = job_status["result"]
            workflow_executions[execution_id]["error"] = job_status["error"]
        else:
            workflow_executions[execution_id] = {
                "status": job_status["status"],
                "results": job_status["result"],
                "error": job_status["error"]
            }
        
        return {
            "execution_id": execution_id,
            "status": job_status["status"],
            "results": job_status["result"],
            "error": job_status["error"]
        }
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        if execution_id not in workflow_executions:
            raise HTTPException(status_code=404, detail="Execution ID not found")
        
        # 如果任务队列不可用，返回本地缓存的状态
        execution = workflow_executions[execution_id]
        return {
            "execution_id": execution_id,
            "status": execution["status"],
            "results": execution["results"],
            "error": execution["error"]
        }

@app.get("/workflows/execution/{execution_id}/results")
async def download_results(execution_id: str):
    
    try:
        # 从任务队列模块获取结果
        task_queue_module_api = module_manager.get_module_api('task_queue')
        if not task_queue_module_api:
            raise HTTPException(status_code=503, detail="Task queue module not available")
        
        job_status = task_queue_module_api.get_job_status(execution_id)
        
        if job_status["status"] != "finished":
            raise HTTPException(status_code=400, detail="Execution is not completed yet")
        
        return JSONResponse(content=job_status["result"])
    except Exception as e:
        logger.error(f"Error getting job results: {e}")
        
        # 如果任务队列不可用，尝试从本地缓存获取
        if execution_id not in workflow_executions:
            raise HTTPException(status_code=404, detail="Execution ID not found")
        
        execution = workflow_executions[execution_id]
        if execution["status"] != "completed":
            raise HTTPException(status_code=400, detail="Execution is not completed yet")
        
        return JSONResponse(content=execution["results"])

# 文件上传接口 - 保留用于AI视频和AI绘图功能
@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    
    try:
        # 读取文件内容
        contents = await file.read()
        
        # 将文件指针重置到开头
        import io
        file.file = io.BytesIO(contents)
        
        file_info = file_handler.upload_file(
            file.file,
            file.content_type,
            file.filename
        )
        return {"message": "File uploaded successfully", "file_info": file_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

# 文件下载接口 - 保留用于获取生成的视频和图像
@app.get("/api/files/download/{file_path:path}")
async def download_file(file_path: str):
    
    file = file_handler.download_file(file_path)
    if file:
        return FileResponse(file, filename=file.name)
    raise HTTPException(status_code=404, detail="File not found")

# 插件管理接口
@app.get("/api/plugins")
async def get_plugins():
    """
    获取所有插件信息
    """
    try:
        plugins = []
        for plugin_id in plugin_manager.get_activated_modules():
            plugin_instance = plugin_manager._modules.get(plugin_id)
            if plugin_instance and plugin_instance.module:
                metadata = plugin_instance.module.metadata
                plugins.append({
                    "id": metadata.id,
                    "name": metadata.name,
                    "version": metadata.version,
                    "description": metadata.description,
                    "status": plugin_instance.state.value
                })
        return JSONResponse(content={"plugins": plugins})
    except Exception as e:
        logger.error(f"Error getting plugins: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plugins/restart_required")
async def check_restart_required():
    """
    检查是否需要重启
    """
    try:
        return JSONResponse(content={"restart_required": False})
    except Exception as e:
        logger.error(f"Error checking restart required: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/upload")
async def upload_plugin(plugin_file: UploadFile = File(...)):
    """
    上传插件文件
    """
    try:
        # 创建临时目录存储插件
        temp_dir = os.path.join(os.path.dirname(__file__), '../../plugins', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存插件文件
        plugin_path = os.path.join(temp_dir, plugin_file.filename)
        with open(plugin_path, 'wb') as f:
            content = await plugin_file.read()
            f.write(content)
        
        # 加载插件
        plugin_id = await plugin_manager.load_plugin(plugin_path)
        if not plugin_id:
            os.remove(plugin_path)
            raise HTTPException(status_code=400, detail="Failed to load plugin")
        
        return JSONResponse(content={"status": "ok", "plugin_id": plugin_id})
    except Exception as e:
        logger.error(f"Error uploading plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/plugins/{plugin_id}")
async def delete_plugin(plugin_id: str):
    """
    删除插件
    """
    try:
        if await plugin_manager.unload_plugin(plugin_id):
            return JSONResponse(content={"status": "ok"})
        else:
            raise HTTPException(status_code=404, detail="Plugin not found")
    except Exception as e:
        logger.error(f"Error deleting plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 环境检测和工具安装接口
@app.get("/api/environment/check")
async def check_environment():
    """
    检查系统环境，列出项目所需的所有工具及其状态
    """
    try:
        environment_status = plugin_manager.check_environment()
        return JSONResponse(content={"status": "success", "environment": environment_status})
    except Exception as e:
        logger.error(f"Error checking environment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/environment/install/{tool_name}")
async def install_tool(tool_name: str):
    """
    安装指定的工具
    """
    try:
        if tool_name == "git":
            success, error_msg = plugin_manager.install_git()
            if success:
                return JSONResponse(content={"status": "success", "message": "Git安装成功"})
            else:
                raise HTTPException(status_code=400, detail=error_msg)
        elif tool_name == "python_packages":
            # 安装Python依赖包
            result = await plugin_manager.install_python_packages()
            return JSONResponse(content=result)
        else:
            raise HTTPException(status_code=400, detail=f"工具 {tool_name} 不支持通过此API安装")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"安装工具 {tool_name} 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 节点管理接口
@app.get("/api/node-manager/repos")
async def get_node_repos():
    """
    获取所有第三方节点仓库
    """
    try:
        if not node_manager_api:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
        repos = node_manager_api["get_third_party_repos"]()
        return JSONResponse(content={"repos": repos})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting node repos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/node-manager/repos")
async def add_node_repo(repo: Dict[str, Any]):
    """
    添加第三方节点仓库
    """
    try:
        if not node_manager_api:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
        node_manager_api["add_third_party_repo"](repo)
        return JSONResponse(content={"status": "ok", "message": "Repository added successfully"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding node repo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/node-manager/repos")
async def remove_node_repo(repo_url: str = Query(...)):
    """
    移除第三方节点仓库
    """
    try:
        if not node_manager_api:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
        node_manager_api["remove_third_party_repo"](repo_url)
        return JSONResponse(content={"status": "ok", "message": "Repository removed successfully"})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing node repo: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/node-manager/install")
async def install_nodes(repo_url: str = Query(...)):
    """
    安装第三方节点
    """
    try:
        if not node_manager_api:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
        result = node_manager_api["install_third_party_nodes"](repo_url)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error installing nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/node-manager/uninstall")
async def uninstall_nodes(repo_name: str = Query(...)):
    """
    卸载第三方节点
    """
    try:
        if not node_manager_api:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
        result = node_manager_api["uninstall_third_party_nodes"](repo_name)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uninstalling nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/node-manager/third-party-nodes")
async def get_third_party_nodes():
    """
    获取已安装的第三方节点
    """
    try:
        if not node_manager_api:
            raise HTTPException(status_code=500, detail="Node manager plugin not activated")
        # 获取所有节点
        all_nodes = node_manager_api["get_all_nodes"]()
        
        # 过滤出第三方节点（这里简化处理，实际可以在节点元数据中添加来源信息）
        third_party_nodes = all_nodes
        
        return JSONResponse(content={"nodes": third_party_nodes})
    except Exception as e:
        logger.error(f"Error getting third-party nodes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/plugins/{plugin_id}/reload")
async def reload_plugin(plugin_id: str):
    """
    重新加载插件
    """
    try:
        new_plugin_id = await plugin_manager.reload_plugin(plugin_id)
        if new_plugin_id:
            return JSONResponse(content={"status": "ok", "plugin_id": new_plugin_id})
        else:
            raise HTTPException(status_code=404, detail="Plugin not found")
    except Exception as e:
        logger.error(f"Error reloading plugin: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket接口 - 用于实时更新工作流状态
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            
            data = await websocket.receive_text()
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "workflow_update":
                
                workflow_data = message.get("workflow")
                room_id = message.get("room_id")
                
                if room_id:
                    await manager.send_room_message(
                        room_id, 
                        {"type": "workflow_update", "client_id": client_id, "workflow": workflow_data}
                    )
                else:
                    await manager.broadcast(
                        {"type": "workflow_update", "client_id": client_id, "workflow": workflow_data}, 
                        exclude_client_id=client_id
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error for client {client_id}: {e}")
        manager.disconnect(client_id)

# 队列信息接口
@app.get("/queue/info")
async def get_queue_info():
    """获取队列信息"""
    try:
        # 从任务队列模块获取队列信息
        task_queue_module_api = module_manager.get_module_api('task_queue')
        if not task_queue_module_api:
            raise HTTPException(status_code=503, detail="Task queue module not available")
        
        queue_info = task_queue_module_api.get_queue_info()
        return JSONResponse(content=queue_info)
    except Exception as e:
        logger.error(f"Error getting queue info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 队列任务列表接口
@app.get("/queue/tasks")
async def get_queue_tasks():
    """获取队列任务列表"""
    try:
        # 从任务队列模块获取任务列表
        task_queue_module_api = module_manager.get_module_api('task_queue')
        if not task_queue_module_api:
            raise HTTPException(status_code=503, detail="Task queue module not available")
        
        queue_tasks = task_queue_module_api.get_queue_tasks()
        return JSONResponse(content=queue_tasks)
    except Exception as e:
        logger.error(f"Error getting queue tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 代理配置接口
@app.get("/api/proxy/config")
async def get_proxy_config():
    """
    获取代理配置
    """
    from api.config_manager.config_manager import config_manager
    proxy_config = config_manager.get("proxy", {})
    return JSONResponse(content=proxy_config)

@app.post("/api/proxy/config")
async def set_proxy_config(config: dict):
    """
    设置代理配置
    """
    try:
        from api.config_manager.config_manager import config_manager
        from api.config_manager.config_manager import ProxyConfig
        
        # 验证配置
        proxy_config = ProxyConfig(**config)
        
        # 更新配置
        for key, value in proxy_config.dict().items():
            config_manager.set(f"proxy.{key}", value)
        
        # 保存配置到文件
        config_manager.save_config_file("app")
        
        return JSONResponse(content={"status": "success", "message": "Proxy configuration updated successfully"})
    except Exception as e:
        logger.error(f"Error setting proxy config: {e}")
        raise HTTPException(status_code=400, detail=str(e))

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the Cognot API server
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    logger.info("Starting server...")
    run_server()

# 挂载前端静态文件（放在所有API路由之后）
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """捕获所有请求，重定向到index.html（单页应用路由）"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Page not found"})
