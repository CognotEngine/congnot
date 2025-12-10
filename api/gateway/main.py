

import sys
import os
import logging

# 设置日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, UploadFile, File, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
from api.realtime.websocket_manager import manager
from api.file_handler.file_handler import file_handler

from core.node_registry import get_all_nodes, load_custom_nodes
from core.task_queue import TaskQueueManager
from core.workflow_manager import WorkflowManager
from core.video_processing_nodes import *  
from core.wan22_nodes import *

import importlib

app = FastAPI(
    title="Cognot AI API",
    description="AI 工作流引擎 API 接口，专注于 AI 绘图和 AI 视频处理",
    version="0.1.0"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有HTTP头
)

# Initialize workflow manager
workflow_manager = WorkflowManager()
# Initialize task queue manager with workflow manager
task_queue_manager = TaskQueueManager(workflow_manager)

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

if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

workflow_executions = {}

workflows = []

class WorkflowDefinition(BaseModel):
    
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]

class ExecutionResponse(BaseModel):
    
    execution_id: str
    status: str
    message: str

class ExecutionStatus(BaseModel):
    
    execution_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None



nodes_metadata_cache = None

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
            from core.node_registry import load_third_party_ai_nodes
            load_third_party_ai_nodes()
            nodes_metadata_cache = None
        except Exception as e:
            print(f"Failed to load third-party AI nodes: {e}")
    
    if nodes_metadata_cache is not None:
        return nodes_metadata_cache
    
    nodes_metadata = get_all_nodes()
    nodes_metadata_cache = nodes_metadata
    
    return nodes_metadata

@app.post("/nodes/load")
async def load_nodes(module_path: str):
    
    try:
        load_custom_nodes(module_path)
        return {"status": "ok", "message": f"Successfully loaded nodes from {module_path}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/workflows/execute", response_model=ExecutionResponse)
async def submit_workflow(
    workflow_def: WorkflowDefinition,
):
    # 处理工作流执行请求
    # 使用任务队列将工作流推送到后台执行
    
    workflow_data = workflow_def.dict()
    execution_id = task_queue_manager.enqueue_workflow(workflow_data)
    
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
        # 从任务队列获取任务状态
        job_status = task_queue_manager.get_job_status(execution_id)
        
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
        # 从任务队列获取结果
        job_status = task_queue_manager.get_job_status(execution_id)
        
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

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """捕获所有请求，重定向到index.html（单页应用路由）"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(status_code=404, content={"detail": "Page not found"})

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the Cognot API server
    """
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
