#!/usr/bin/env python3
"""
Cognot AI Workflow Engine - Task Queue Worker

This script runs a worker process that consumes tasks from the Redis Queue.
It executes AI inference tasks (like Stable Diffusion) in a separate process,
preventing the FastAPI server from being blocked by slow AI tasks.
"""

import logging
import sys
import os
from rq import Worker, Queue
from redis import Redis

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

# Import the execute_workflow_task function that we want to execute
from core.task_queue import execute_workflow_task

def main():
    """Main function to start the worker"""
    try:
        # Connect to Redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        redis_conn = Redis.from_url(redis_url)
        
        logger.info(f"Connecting to Redis at {redis_url}")
        
        # Create the queue
        queue = Queue('cognot-tasks', connection=redis_conn)
        
        # Start the worker
        logger.info("Starting Cognot worker...")
        logger.info("Waiting for tasks...")
        
        # Create worker and start processing tasks
        worker = Worker([queue], connection=redis_conn)
        worker.work()
            
    except Exception as e:
        logger.error(f"Failed to start worker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
