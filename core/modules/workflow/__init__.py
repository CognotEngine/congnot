# Workflow Module

import logging
from core.module.module_registrar import ModuleRegistrationOptions, register_module
from core.module.module_registrar import create_module_api
from core.workflow_manager import WorkflowManager

# Create module logger
logger = logging.getLogger(__name__)


# Workflow module API
def validate_workflow(workflow_data):
    """
    Validate workflow data
    
    Args:
        workflow_data: Workflow data
        
    Returns:
        Dictionary containing is_valid and errors
    """
    errors = []

    # Check basic workflow structure
    if not isinstance(workflow_data, dict):
        errors.append('Workflow data must be a dictionary')
        return {'is_valid': False, 'errors': errors}

    # Check if contains nodes field
    if 'nodes' not in workflow_data:
        errors.append('Workflow data must contain "nodes" field')
        return {'is_valid': False, 'errors': errors}

    if not isinstance(workflow_data['nodes'], list):
        errors.append('"nodes" field must be a list')
        return {'is_valid': False, 'errors': errors}

    # Check if contains edges field (if any)
    if 'edges' in workflow_data and not isinstance(workflow_data['edges'], list):
        errors.append('"edges" field must be a list')
        return {'is_valid': False, 'errors': errors}

    return {'is_valid': True, 'errors': errors}


def export_workflow(workflow_data):
    """
    Export workflow
    
    Args:
        workflow_data: Workflow data
        
    Returns:
        JSON string of the workflow
    """
    import json
    return json.dumps(workflow_data, indent=2)


def import_workflow(workflow_json):
    """
    Import workflow
    
    Args:
        workflow_json: JSON string of the workflow
        
    Returns:
        Dictionary containing success, workflow, and errors
    """
    import json
    
    try:
        workflow_data = json.loads(workflow_json)
        validation = validate_workflow(workflow_data)
        
        if not validation['is_valid']:
            return {'success': False, 'errors': validation['errors']}

        return {'success': True, 'workflow': workflow_data}
    except json.JSONDecodeError as e:
        return {'success': False, 'errors': [f'Invalid JSON format: {e}']}
    except Exception as e:
        return {'success': False, 'errors': [f'Unknown error: {e}']}


# Create WorkflowManager instance
workflow_manager = WorkflowManager()

# Workflow module API
workflow_api = {
    'validate_workflow': validate_workflow,
    'export_workflow': export_workflow,
    'import_workflow': import_workflow,
    'workflow_manager': workflow_manager
}


# Module activation function
def activate_workflow_module():
    logger.info('Activating workflow module...')
    # Initialization code can be added here when module is activated


# Module deactivation function
def deactivate_workflow_module():
    logger.info('Deactivating workflow module...')
    # Cleanup code can be added here when module is deactivated


# Register workflow module
register_module(ModuleRegistrationOptions(
    id='workflow',
    name='Workflow Module',
    version='1.0.0',
    description='Core workflow management module',
    dependencies=[],  # Can specify other module IDs that are dependencies
    activate=activate_workflow_module,
    deactivate=deactivate_workflow_module,
    get_api=create_module_api(workflow_api)
))
