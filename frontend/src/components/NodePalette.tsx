import React, { useState, useEffect } from 'react';
import './NodePalette.css';
import { WorkflowNode, WorkflowEdge, NodeParam, NodePort, NodeConfig, PaletteNode as TypePaletteNode, SavedWorkflow } from '../types';
import { useI18n } from '../contexts/I18nContext';

const NODE_ICONS = {
  input: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" y1="15" x2="12" y2="3" /></svg>,
  output: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-4a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v4" /><polyline points="12 3 17 8 12 13" /><line x1="7" y1="8" x2="17" y2="8" /></svg>,
  processing: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" /></svg>,
  math: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z" /><line x1="9" y1="10" x2="15" y2="10" /><line x1="9" y1="14" x2="15" y2="14" /></svg>,
  string: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></svg>,
  logic: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>,
  control: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9" /></svg>,
  basic: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" /></svg>,
  general: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" /></svg>,
  preset: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><line x1="3" y1="9" x2="21" y2="9" /><line x1="9" y1="21" x2="9" y2="9" /></svg>,
  ai: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a10 10 0 1 0 10 10A10 10 0 0 0 12 2z" /><path d="M12 6v6l4 2" /></svg>,
  video: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="23 7 16 12 23 17 23 7" /><rect x="1" y="5" width="15" height="14" rx="2" ry="2" /></svg>
};

// 使用导入的类型接口
interface PaletteNode extends TypePaletteNode {
  params?: Record<string, NodeParam>;
  workflowData?: SavedWorkflow;
}

interface Category {
  id: string;
  name: string;
  icon: React.ReactNode;
  nodes: PaletteNode[];
}

interface NodePaletteProps {
  setNodes: (nodes: WorkflowNode[]) => void;
  setEdges: (edges: WorkflowEdge[]) => void;
}

function NodePalette({ setNodes, setEdges }: NodePaletteProps) {
  // 使用i18n上下文
  const { t, currentLanguage } = useI18n();
  
  const [expandedCategories, setExpandedCategories] = useState<string[]>(['general', 'presets']);
  
  const [nodeCategories, setNodeCategories] = useState<Category[]>([]);
  
  const [originalNodeCategories, setOriginalNodeCategories] = useState<Category[]>([]);
  
  const [savedWorkflows, setSavedWorkflows] = useState<SavedWorkflow[]>([]);
  
  const [loading, setLoading] = useState<boolean>(true);
  
  const [searchKeyword, setSearchKeyword] = useState<string>('');
  
  const [showSearchResults, setShowSearchResults] = useState<boolean>(false);
  
  const [searchResults, setSearchResults] = useState<(PaletteNode & { categoryName: string; categoryIcon: React.ReactNode })[]>([]);

  
  
  useEffect(() => {
    console.log('NodePalette useEffect called with language:', currentLanguage);
    const initializeApp = async () => {
      try {
        setLoading(true);
        
        // 从 node-config.json 文件加载新注册的节点
        const response = await fetch('/node-config.json');
        const nodesData = await response.json();
        
        // 将 nodes.json 中的节点转换为调色板节点格式
        interface PaletteNodeWithCategory extends PaletteNode {
          category?: string;
        }
        
        const newNodes: PaletteNodeWithCategory[] = Object.entries(nodesData).map(([nodeId, nodeInfo]: [string, any]) => {
          // 转换输入端口
          const inputs = nodeInfo.inputs ? Object.entries(nodeInfo.inputs).map(([inputId, inputType]) => ({
            id: inputId,
            type: String(inputType),
            label: inputId
          })) : [];
          
          // 转换输出端口
          const outputs = nodeInfo.outputs ? Object.entries(nodeInfo.outputs).map(([outputId, outputType]) => ({
            id: outputId,
            type: String(outputType),
            label: outputId
          })) : [];
          
          // 转换参数配置
          const params: Record<string, NodeParam> = {};
          if (nodeInfo.input_schema && nodeInfo.input_schema.properties) {
            Object.entries(nodeInfo.input_schema.properties).forEach(([paramName, paramSchema]: [string, any]) => {
              params[paramName] = {
                name: paramName,
                type: paramSchema.type || 'string',
                value: paramSchema.default || '',
                label: paramSchema.title || paramName,
                description: paramSchema.description || '',
                widget_meta: paramSchema.widget_meta || {
                  widget_type: 'text_input',
                  options: []
                }
              };
            });
          }
          
          return {
            id: nodeId,
            type: nodeId,
            label: nodeInfo.name || nodeId,
            description: nodeInfo.description || '',
            config: {},
            inputs,
            outputs,
            params,
            category: nodeInfo.category // 保存节点的category属性
          };
        });
        
        // 定义节点分类
        const aiCategories: Category[] = [
          {
            id: 'input_output',
            name: t('nodePalette.Input/Output'),
            icon: NODE_ICONS.general,
            nodes: [
              {
                id: 'imageInput',
                type: 'imageInput',
                label: t('nodePalette.Image Input'),
                description: t('nodePalette.Image Input description'),
                config: {},
                inputs: [],
                outputs: [
                  { id: 'image', type: 'image', label: t('nodePalette.Image') },
                  { id: 'mask', type: 'image', label: t('nodePalette.Mask') }
                ]
              },
              {
                id: 'imageOutput',
                type: 'imageOutput',
                label: t('nodePalette.Image Output'),
                description: t('nodePalette.Image Output node'),
                config: {},
                inputs: [{ id: 'input', type: 'string', label: t('nodePalette.Input') }],
                outputs: []
              },
              {
                id: 'saveImage',
                type: 'saveImage',
                label: t('nodePalette.Save Image'),
                description: t('nodePalette.Save Image description'),
                config: {},
                inputs: [{ id: 'image', type: 'image', label: t('nodePalette.Image') }],
                outputs: []
              },
              {
                id: 'previewNode',
                type: 'previewNode',
                label: t('nodePalette.Preview Image'),
                description: t('nodePalette.Preview Image description'),
                config: {},
                inputs: [{ id: 'image', type: 'image', label: t('nodePalette.Image') }],
                outputs: [{ id: 'image', type: 'image', label: t('nodePalette.Image') }]
              }
            ]
          },
          {
            id: 'text_processing',
            name: t('nodePalette.Text Processing'),
            icon: NODE_ICONS.string,
            nodes: [
              {
                id: 'promptInterpolator',
                type: 'promptInterpolator',
                label: t('nodePalette.Prompt Interpolator'),
                description: t('nodePalette.Prompt Interpolator description'),
                config: {},
                inputs: [
                  { id: 'frame_info', type: 'object', label: t('nodePalette.Frame Info') }
                ],
                outputs: [
                  { id: 'interpolated_prompt', type: 'string', label: t('nodePalette.Interpolated Prompt') }
                ],
                params: {
                  interpolationMethod: {
                    name: 'interpolationMethod',
                    type: 'string',
                    value: 'linear',
                    label: t('nodePalette.interpolationMethod'),
                    description: '选择提示文本插值方法',
                    widget_meta: {
                      widget_type: 'select',
                      options: [
                        { value: 'linear', label: '线性' },
                        { value: 'smoothstep', label: '平滑' },
                        { value: 'ease_in_out', label: '缓进缓出' },
                        { value: 'catmull_rom', label: 'Catmull-Rom' }
                      ]
                    }
                  },
                  strength: {
                    name: 'strength',
                    type: 'number',
                    value: 0.5,
                    label: t('nodePalette.interpolationStrength'),
                    description: '设置插值强度',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 1,
                      step: 0.01
                    }
                  },
                  smoothness: {
                    name: 'smoothness',
                    type: 'number',
                    value: 1.0,
                    label: t('nodePalette.smoothness'),
                    description: '设置平滑度',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 5,
                      step: 0.1
                    }
                  }
                }
              }
            ]
          },
          {
            id: 'image_generation',
            name: t('nodePalette.Image Generation'),
            icon: NODE_ICONS.ai,
            nodes: [
              {                id: 'stable_diffusion_generate',                type: 'stable_diffusion_generate',                label: t('nodePalette.Stable Diffusion Generate'),                description: t('nodePalette.Stable Diffusion Generate description'),                config: {},                inputs: [                  { id: 'prompt', type: 'string', label: t('nodePalette.Prompt') },                  { id: 'negative_prompt', type: 'string', label: t('nodePalette.Negative Prompt') },                  { id: 'height', type: 'number', label: t('nodePalette.Height') },                  { id: 'width', type: 'number', label: t('nodePalette.Width') },                  { id: 'num_inference_steps', type: 'number', label: t('nodePalette.Inference Steps') },                  { id: 'guidance_scale', type: 'number', label: t('nodePalette.Guidance Scale') },                  { id: 'seed', type: 'number', label: t('nodePalette.Seed') }                ],                outputs: [                  { id: 'image', type: 'string', label: t('nodePalette.Image') },                  { id: 'success', type: 'boolean', label: t('nodePalette.Success') },                  { id: 'message', type: 'string', label: t('nodePalette.Message') }                ]              },
              {
                id: 'stable_diffusion_image_to_image',
                type: 'stable_diffusion_image_to_image',
                label: t('nodePalette.Stable Diffusion Image To Image'),
                description: t('nodePalette.Stable Diffusion Image To Image description'),
                config: {},
                inputs: [
                  { id: 'prompt', type: 'string', label: t('nodePalette.Prompt') },
                  { id: 'negative_prompt', type: 'string', label: t('nodePalette.Negative Prompt') },
                  { id: 'init_image', type: 'string', label: t('nodePalette.Initial Image') },
                  { id: 'strength', type: 'number', label: t('nodePalette.Strength') },
                  { id: 'num_inference_steps', type: 'number', label: t('nodePalette.Inference Steps') },
                  { id: 'guidance_scale', type: 'number', label: t('nodePalette.Guidance Scale') },
                  { id: 'seed', type: 'number', label: t('nodePalette.Seed') }
                ],
                outputs: [
                  { id: 'image', type: 'string', label: t('nodePalette.Image') },
                  { id: 'success', type: 'boolean', label: t('nodePalette.Success') },
                  { id: 'message', type: 'string', label: t('nodePalette.Message') }
                ]
              },
              {
                id: 'imageManipulation',
                type: 'imageManipulation',
                label: t('nodePalette.Image Manipulation'),
                description: t('nodePalette.Image Manipulation description'),
                config: {},
                inputs: [{ id: 'image', type: 'image', label: t('nodePalette.Image') }],
                outputs: [{ id: 'image', type: 'image', label: t('nodePalette.Image') }]
              },
              {
                id: 'vaeDecode',
                type: 'vaeDecode',
                label: t('nodePalette.VAE Decode'),
                description: t('nodePalette.VAE Decode description'),
                config: {},
                inputs: [{ id: 'latent', type: 'object', label: t('nodePalette.Latent') }],
                outputs: [{ id: 'image', type: 'image', label: t('nodePalette.Image') }]
              },
              {
                id: 'fusionImage',
                type: 'fusionImage',
                label: t('nodePalette.Fusion Image'),
                description: t('nodePalette.Fusion Image description'),
                config: {},
                inputs: [
                  { id: 'generated_image', type: 'image', label: t('nodePalette.Generated Image') },
                  { id: 'original_image', type: 'image', label: t('nodePalette.Original Image') },
                  { id: 'fusion_mask', type: 'image', label: t('nodePalette.Fusion Mask') }
                ],
                outputs: [
                  { id: 'fused_image', type: 'image', label: t('nodePalette.Fused Image') }
                ],
                params: {
                  fusionMethod: {
                    name: 'fusionMethod',
                    type: 'string',
                    value: 'alpha_blend',
                    label: t('nodePalette.fusionMethod'),
                    description: '选择图像融合方法',
                    widget_meta: {
                      widget_type: 'select',
                      options: [
                        { value: 'alpha_blend', label: 'Alpha 混合' },
                        { value: 'masked_blend', label: '遮罩混合' },
                        { value: 'laplacian', label: '拉普拉斯金字塔' },
                        { value: 'gradient', label: '梯度混合' }
                      ]
                    }
                  },
                  alpha: {
                    name: 'alpha',
                    type: 'number',
                    value: 0.5,
                    label: t('nodePalette.blendRatio'),
                    description: '设置混合比例',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 1,
                      step: 0.01
                    }
                  },
                  maskSmoothness: {
                    name: 'maskSmoothness',
                    type: 'number',
                    value: 1.0,
                    label: t('nodePalette.maskSmoothness'),
                    description: '设置遮罩平滑度',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 5,
                      step: 0.1
                    }
                  },
                  preserveDetails: {
                    name: 'preserveDetails',
                    type: 'boolean',
                    value: false,
                    label: t('nodePalette.preserveDetails'),
                    description: '是否保留细节',
                    widget_meta: {
                      widget_type: 'checkbox'
                    }
                  },
                  detailPreservationLevel: {
                    name: 'detailPreservationLevel',
                    type: 'number',
                    value: 0.5,
                    label: t('nodePalette.detailPreservationLevel'),
                    description: '设置细节保留级别',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 1,
                      step: 0.01
                    }
                  }
                }
              }
            ]
          },
          {
            id: 'video_processing',
            name: t('nodePalette.Video Processing'),
            icon: NODE_ICONS.ai,
            nodes: [
              {
                id: 'videoLoad',
                type: 'videoLoad',
                label: t('nodePalette.Video/Image Load'),
                description: t('nodePalette.Video/Image Load description'),
                config: {},
                inputs: [],
                outputs: [
                  { id: 'image', type: 'image', label: t('nodePalette.Image') },
                  { id: 'video_info', type: 'object', label: t('nodePalette.Video Info') }
                ],
                params: {
                  videoPath: {
                    name: 'videoPath',
                    type: 'string',
                    value: '',
                    label: t('nodePalette.videoPath'),
                    description: '选择或输入视频文件路径',
                    widget_meta: {
                      widget_type: 'text'
                    }
                  },
                  frameRate: {
                    name: 'frameRate',
                    type: 'number',
                    value: 24,
                    label: '帧率',
                    description: '视频帧率',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 1,
                      max_value: 60,
                      step: 1
                    }
                  },
                  totalFrames: {
                    name: 'totalFrames',
                    type: 'number',
                    value: 100,
                    label: t('nodePalette.totalFrames'),
                    description: '视频总帧数',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 1,
                      max_value: 1000,
                      step: 1
                    }
                  },
                  resolution: {
                    name: 'resolution',
                    type: 'object',
                    value: { width: 1920, height: 1080 },
                    label: t('nodePalette.resolution'),
                    description: '视频分辨率',
                    widget_meta: {
                      widget_type: 'text'
                    }
                  }
                }
              },
              {
                id: 'frameIndexManager',
                type: 'frameIndexManager',
                label: t('nodePalette.Frame Index Manager'),
                description: t('nodePalette.Frame Index Manager description'),
                config: {},
                inputs: [],
                outputs: [
                  { id: 'frame_info', type: 'object', label: t('nodePalette.Frame Info') },
                  { id: 'progress', type: 'number', label: t('nodePalette.Progress') },
                  { id: 'flags', type: 'object', label: t('nodePalette.Flags') }
                ],
                params: {
                  totalFrames: {
                    name: 'totalFrames',
                    type: 'number',
                    value: 100,
                    label: '总帧数',
                    description: '视频总帧数',
                    widget_meta: {
                      widget_type: 'number',
                      min_value: 1,
                      max_value: 10000
                    }
                  },
                  currentFrame: {
                    name: 'currentFrame',
                    type: 'number',
                    value: 0,
                    label: t('nodePalette.currentFrame'),
                    description: '当前处理的帧',
                    widget_meta: {
                      widget_type: 'number',
                      min_value: 0,
                      max_value: 9999
                    }
                  }
                }
              },
              {
                id: 'opticalFlowCalculator',
                type: 'opticalFlowCalculator',
                label: t('nodePalette.Optical Flow Calculator'),
                description: t('nodePalette.Optical Flow Calculator description'),
                config: {},
                inputs: [
                  { id: 'prev_frame', type: 'image', label: t('nodePalette.Previous Frame') },
                  { id: 'current_frame', type: 'image', label: t('nodePalette.Current Frame') }
                ],
                outputs: [
                  { id: 'flow_field', type: 'image', label: t('nodePalette.Flow Field') },
                  { id: 'motion_mask', type: 'image', label: t('nodePalette.Motion Mask') },
                  { id: 'visualization', type: 'image', label: t('nodePalette.Visualization') }
                ],
                params: {
                  method: {
                    name: 'method',
                    type: 'string',
                    value: 'farneback',
                    label: t('nodePalette.method'),
                    description: '选择光流计算方法',
                    widget_meta: {
                      widget_type: 'select',
                      options: [
                        { value: 'farneback', label: 'Farneback' },
                        { value: 'lucas_kanade', label: 'Lucas-Kanade' },
                        { value: 'dense', label: 'Dense' }
                      ]
                    }
                  },
                  quality: {
                    name: 'quality',
                    type: 'string',
                    value: 'medium',
                    label: t('nodePalette.quality'),
                    description: '选择计算质量',
                    widget_meta: {
                      widget_type: 'select',
                      options: [
                        { value: 'low', label: '低' },
                        { value: 'medium', label: '中' },
                        { value: 'high', label: '高' }
                      ]
                    }
                  },
                  maxFlow: {
                    name: 'maxFlow',
                    type: 'number',
                    value: 20,
                    label: t('nodePalette.maxFlow'),
                    description: '设置最大流量值',
                    widget_meta: {
                      widget_type: 'number',
                      min_value: 1,
                      max_value: 100
                    }
                  },
                  showVisualization: {
                    name: 'showVisualization',
                    type: 'boolean',
                    value: false,
                    label: t('nodePalette.showVisualization'),
                    description: '是否显示光流可视化',
                    widget_meta: {
                      widget_type: 'checkbox'
                    }
                  }
                }
              },
              {
                id: 'frameProcessorLoop',
                type: 'frameProcessorLoop',
                label: t('nodePalette.Frame Processor Loop'),
                description: t('nodePalette.Frame Processor Loop description'),
                config: {},
                inputs: [
                  { id: 'initial_frame', type: 'image', label: t('nodePalette.Initial Frame') },
                  { id: 'prompt', type: 'string', label: t('nodePalette.Prompt') },
                  { id: 'flow_field', type: 'image', label: t('nodePalette.Flow Field') }
                ],
                outputs: [
                  { id: 'generated_frame', type: 'image', label: t('nodePalette.Generated Frame') },
                  { id: 'latent_output', type: 'object', label: t('nodePalette.Latent Output') }
                ],
                params: {
                  iterations: {
                    name: 'iterations',
                    type: 'number',
                    value: 50,
                    label: t('nodePalette.samplingIterations'),
                    description: '设置采样迭代次数',
                    widget_meta: {
                      widget_type: 'number',
                      min_value: 1,
                      max_value: 200
                    }
                  },
                  denoiseStrength: {
                    name: 'denoiseStrength',
                    type: 'number',
                    value: 0.7,
                    label: t('nodePalette.denoiseStrength'),
                    description: '设置去噪强度',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 1,
                      step: 0.01
                    }
                  },
                  guidanceScale: {
                    name: 'guidanceScale',
                    type: 'number',
                    value: 7.5,
                    label: t('nodePalette.guidanceScale'),
                    description: '设置引导缩放',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 20,
                      step: 0.1
                    }
                  },
                  seed: {
                    name: 'seed',
                    type: 'number',
                    value: -1,
                    label: t('nodePalette.seed'),
                    description: '设置随机种子，-1表示随机',
                    widget_meta: {
                      widget_type: 'number',
                      min_value: -1,
                      max_value: 999999999
                    }
                  },
                  useMotionBlending: {
                    name: 'useMotionBlending',
                    type: 'boolean',
                    value: false,
                    label: t('nodePalette.useMotionBlending'),
                    description: '是否启用运动融合',
                    widget_meta: {
                      widget_type: 'checkbox'
                    }
                  },
                  motionBlendingStrength: {
                    name: 'motionBlendingStrength',
                    type: 'number',
                    value: 0.5,
                    label: t('nodePalette.motionBlendingStrength'),
                    description: '设置运动融合强度',
                    widget_meta: {
                      widget_type: 'slider',
                      min_value: 0,
                      max_value: 1,
                      step: 0.01
                    }
                  }
                }
              },
              {
                id: 'videoComposer',
                type: 'videoComposer',
                label: t('nodePalette.Video Composer'),
                description: t('nodePalette.Video Composer description'),
                config: {},
                inputs: [
                  { id: 'frames', type: 'array', label: t('nodePalette.Frames') }
                ],
                outputs: [
                  { id: 'video', type: 'string', label: t('nodePalette.Video') }
                ],
                params: {
                  outputFormat: {
                    name: 'outputFormat',
                    type: 'string',
                    value: 'mp4',
                    label: t('nodePalette.outputFormat'),
                    description: '选择视频输出格式',
                    widget_meta: {
                      widget_type: 'select',
                      options: [
                        { value: 'mp4', label: 'MP4' },
                        { value: 'webm', label: 'WebM' },
                        { value: 'avi', label: 'AVI' },
                        { value: 'mov', label: 'MOV' }
                      ]
                    }
                  },
                  fps: {
                    name: 'fps',
                    type: 'number',
                    value: 24,
                    label: t('nodePalette.fps'),
                    description: '设置视频帧率',
                    widget_meta: {
                      widget_type: 'number',
                      min_value: 1,
                      max_value: 60
                    }
                  },
                  bitrate: {
                    name: 'bitrate',
                    type: 'string',
                    value: '10M',
                    label: t('nodePalette.bitrate'),
                    description: '设置视频比特率',
                    widget_meta: {
                      widget_type: 'text'
                    }
                  },
                  codec: {
                    name: 'codec',
                    type: 'string',
                    value: 'h264',
                    label: t('nodePalette.codec'),
                    description: '选择视频编码',
                    widget_meta: {
                      widget_type: 'select',
                      options: [
                        { value: 'h264', label: 'H.264' },
                        { value: 'h265', label: 'H.265' },
                        { value: 'vp9', label: 'VP9' },
                        { value: 'av1', label: 'AV1' }
                      ]
                    }
                  },
                  outputPath: {
                    name: 'outputPath',
                    type: 'string',
                    value: '',
                    label: t('nodePalette.outputPath'),
                    description: '设置视频保存路径',
                    widget_meta: {
                      widget_type: 'text'
                    }
                  }
                }
              }
            ]
          }
        ];
        
        // 根据节点的category属性将节点分配到对应的分类
        const categorizedNodes = [...aiCategories];
        
        newNodes.forEach(node => {
          // 获取节点的category属性
          const nodeCategory = node.category;
          
          // 找到对应的分类
          const targetCategory = categorizedNodes.find(cat => {
            if (nodeCategory === 'output' && cat.id === 'postprocessing') {
              return true; // 将output分类的节点放到Post-Processing & Output分类
            }
            if (nodeCategory === 'input' && cat.id === 'input_output') {
              return true; // 将input分类的节点放到Input/Output分类
            }
            if (nodeCategory === 'ai' && cat.id === 'image_generation') {
              return true; // 将ai分类的节点放到Image Generation分类
            }
            // 检查节点类型是否与视频处理相关
            if (nodeCategory === 'video' || node.type.includes('video') || node.type.includes('Video')) {
              return cat.id === 'video_processing'; // 将视频相关节点放到Video Processing分类
            }
            // 检查节点类型是否与文本处理相关
            if (nodeCategory === 'text' || node.type.includes('text') || node.type.includes('Text')) {
              return cat.id === 'text_processing'; // 将文本相关节点放到Text Processing分类
            }
            return cat.id === nodeCategory;
          });
          
          if (targetCategory) {
            // 添加节点到对应的分类
            targetCategory.nodes.push(node);
          } else {
            // 如果没有找到对应的分类，默认将节点添加到图像生成分类
            const defaultCategory = categorizedNodes.find(cat => cat.id === 'image_generation');
            if (defaultCategory) {
              defaultCategory.nodes.push(node);
            }
          }
        });
        
        // 设置节点分类
        setNodeCategories(categorizedNodes);
        setOriginalNodeCategories(categorizedNodes);
        
        // 默认展开所有分类
        const categoriesToExpand = aiCategories.map(category => category.id);
        setExpandedCategories(categoriesToExpand);
        
      } catch (error) {
        console.error('Error initializing app:', error);
      } finally {
        setLoading(false);
        loadSavedWorkflows();
      }
    };
    
    initializeApp();
  }, [currentLanguage, t]); 
  
  
  useEffect(() => {
    if (savedWorkflows.length > 0) {
      setNodeCategories(prevCategories => {
        const updatedCategories = [...prevCategories];
        const presetsIndex = updatedCategories.findIndex(cat => cat.id === 'presets');
        
        if (presetsIndex !== -1) {
          
          updatedCategories[presetsIndex] = {
            ...updatedCategories[presetsIndex],
            nodes: savedWorkflows.map(workflow => ({
              id: workflow.id,
              type: 'preset',
              label: workflow.name,
              description: `Created: ${new Date(workflow.createdAt).toLocaleString()}`,
              category: 'presets',
              workflowData: workflow
            }))
          };
        }
        
        return updatedCategories;
      });
      
      
      setOriginalNodeCategories(prevCategories => {
        const updatedCategories = [...prevCategories];
        const presetsIndex = updatedCategories.findIndex(cat => cat.id === 'presets');
        
        if (presetsIndex !== -1) {
          
          updatedCategories[presetsIndex] = {
            ...updatedCategories[presetsIndex],
            nodes: savedWorkflows.map(workflow => ({
              id: workflow.id,
              type: 'preset',
              label: workflow.name,
              description: `Created: ${new Date(workflow.createdAt).toLocaleString()}`,
              category: 'presets',
              workflowData: workflow
            }))
          };
        }
        
        return updatedCategories;
      });
    }
  }, [savedWorkflows]);
  
  
  const handleSearchChange = (e: { target: { value: string } }) => {
    const keyword = e.target.value;
    setSearchKeyword(keyword);
    
    if (keyword.trim() === '') {
      setShowSearchResults(false);
      setNodeCategories(originalNodeCategories);
      return;
    }
    
    
    interface NodeWithCategoryInfo {
      id: string;
      type: string;
      label: string;
      description: string;
      category?: string;
      config?: NodeConfig;
      inputs?: NodePort[];
      outputs?: NodePort[];
      icon?: React.ReactNode;
      workflowData?: SavedWorkflow;
      categoryName: string;
      categoryIcon: React.ReactNode;
    }
    
    const allNodes: NodeWithCategoryInfo[] = [];
    originalNodeCategories.forEach(category => {
      category.nodes.forEach(node => {
        allNodes.push({
          ...node,
          categoryName: category.name,
          categoryIcon: category.icon
        } as NodeWithCategoryInfo);
      });
    });
    
    
    const filteredNodes = allNodes.filter(node => 
      node.label.toLowerCase().includes(keyword.toLowerCase()) || 
      node.description.toLowerCase().includes(keyword.toLowerCase()) ||
      node.type.toLowerCase().includes(keyword.toLowerCase())
    );
    
    setSearchResults(filteredNodes);
    setShowSearchResults(true);
  };
  
  

  
  
  const toggleCategory = (categoryId: string): void => {
    setExpandedCategories(prev => 
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };
  
  
  const onDragStart = (event: React.DragEvent<HTMLDivElement>, node: PaletteNode): void => {
    // Create a custom node data object compatible with React Flow
    // NOTE: This application ONLY uses custom nodes. No React Flow built-in node types are created or used.
    const reactFlowNode: WorkflowNode = {
      id: `node_${Date.now()}`,
      type: node.type, // Custom node type - DO NOT use React Flow built-in node types
      position: { x: 0, y: 0 },
      data: {
        label: node.label,
        description: node.description,
        category: node.category,
        icon: node.icon,
        outputs: node.outputs || [],
        inputs: node.inputs || [],
        config: node.config,
        params: node.params || {} // 添加params信息到拖拽节点数据中
      }
    };
    
    // Set the drag data with the node information in React Flow format
    event.dataTransfer.setData('application/reactflow', JSON.stringify(reactFlowNode));
    
    event.dataTransfer.effectAllowed = 'move';
  };
  
  
  const handlePresetClick = (node: PaletteNode): void => {
    if (node.type === 'preset' && node.workflowData) {
      // Since we don't have handleLoadWorkflow, let's implement the logic directly
      try {
        // Load the workflow from localStorage
        const workflows = JSON.parse(localStorage.getItem('savedWorkflows') || '[]') as Array<any>;
        const workflow = workflows.find(w => w.id === node.workflowData?.id);
        
        if (workflow && workflow.data) {
          setNodes(workflow.data.nodes);
          setEdges(workflow.data.edges);
        }
      } catch (error) {
        console.error('Failed to load workflow preset:', error);
      }
    }
  };
  
  
  const loadSavedWorkflows = (): void => {
    try {
      let workflows = JSON.parse(localStorage.getItem('savedWorkflows') || '[]') as Array<any>;
      
      // 清除localStorage中的示例工作流
      workflows = workflows.filter(workflow => workflow.id !== 'sd-example-workflow');
      
      // Map workflows to match the Workflow interface (nodes and edges under data)
      const formattedWorkflows = workflows.map(workflow => ({
        id: workflow.id,
        name: workflow.name,
        data: {
          nodes: workflow.data?.nodes || workflow.nodes || [],
          edges: workflow.data?.edges || workflow.edges || []
        },
        createdAt: workflow.createdAt || new Date().toISOString()
      }));
      
      // Update localStorage with formatted workflows
      localStorage.setItem('savedWorkflows', JSON.stringify(formattedWorkflows));
      
      setSavedWorkflows(formattedWorkflows);
      updatePresetsCategory(formattedWorkflows);
    } catch (error) {
      console.error('Error loading saved workflows:', error);
    }
  };
  
  
  const updatePresetsCategory = (workflows: SavedWorkflow[]): void => {
    
    // Only update presets category if we already have categories from backend or defaults
    if (nodeCategories.length > 0 || originalNodeCategories.length > 0) {
      setNodeCategories(prevCategories => {
        const updatedCategories = [...prevCategories];
        const presetsIndex = updatedCategories.findIndex(cat => cat.id === 'presets');
        
        if (presetsIndex !== -1) {
          // Update existing presets category
          updatedCategories[presetsIndex] = {
            ...updatedCategories[presetsIndex],
            nodes: workflows.map(workflow => ({
              id: workflow.id,
              type: 'preset',
              label: workflow.name,
              description: `创建于: ${new Date(workflow.createdAt).toLocaleString()}`,
              category: 'presets',
              workflowData: workflow
            }))
          };
        } else if (workflows.length > 0) {
          // Add presets category only if we have workflows
          updatedCategories.push({
            id: 'presets',
            name: 'Presets',
            icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /><line x1="10" y1="13" x2="8" y2="13" /><line x1="16" y1="13" x2="14" y2="13" /><line x1="14" y1="17" x2="8" y2="17" /><line x1="16" y1="17" x2="22" y2="17" /><line x1="14" y1="9" x2="22" y2="9" /></svg>,
            nodes: workflows.map(workflow => ({
              id: workflow.id,
              type: 'preset',
              label: workflow.name,
              description: `创建于: ${new Date(workflow.createdAt).toLocaleString()}`,
              category: 'presets',
              workflowData: workflow
            }))
          });
        }
        
        return updatedCategories;
      });
      
      setOriginalNodeCategories(prevCategories => {
        const updatedCategories = [...prevCategories];
        const presetsIndex = updatedCategories.findIndex(cat => cat.id === 'presets');
        
        if (presetsIndex !== -1) {
          // Update existing presets category
          updatedCategories[presetsIndex] = {
            ...updatedCategories[presetsIndex],
            nodes: workflows.map(workflow => ({
              id: workflow.id,
              type: 'preset',
              label: workflow.name,
              description: `创建于: ${new Date(workflow.createdAt).toLocaleString()}`,
              category: 'presets',
              workflowData: workflow
            }))
          };
        } else if (workflows.length > 0) {
          // Add presets category only if we have workflows
          updatedCategories.push({
            id: 'presets',
            name: 'Presets',
            icon: <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /><line x1="10" y1="13" x2="8" y2="13" /><line x1="16" y1="13" x2="14" y2="13" /><line x1="14" y1="17" x2="8" y2="17" /><line x1="16" y1="17" x2="22" y2="17" /><line x1="14" y1="9" x2="22" y2="9" /></svg>,
            nodes: workflows.map(workflow => ({
              id: workflow.id,
              type: 'preset',
              label: workflow.name,
              description: `创建于: ${new Date(workflow.createdAt).toLocaleString()}`,
              category: 'presets',
              workflowData: workflow
            }))
          });
        }
        
        return updatedCategories;
      });
    }
  }
  
  
  // We'll now use React Flow's own state management, so we don't need these functions
  
  
  // Commented out unused function
  /*const handleSaveWorkflow = (): void => {
    
    const workflowData = {
      nodes: nodes,
      edges: edges
    };
    
    
    if (workflowData.nodes.length > 0 || workflowData.edges.length > 0) {
      
      const workflowId = `workflow_${Date.now()}`;
      const workflowName = prompt('Please enter workflow name:', 'My Workflow');
      
      if (workflowName) {
        
        const workflows = JSON.parse(localStorage.getItem('savedWorkflows') || '[]');
        
        
        workflows.push({
          id: workflowId,
          name: workflowName,
          data: workflowData,
          createdAt: new Date().toISOString()
        });
        
        
        localStorage.setItem('savedWorkflows', JSON.stringify(workflows));
        
        
        loadSavedWorkflows();
        alert('Workflow saved!');
      }
    } else {
      alert('No workflow to save');
    }
  };*/
  
  
  const handleDeleteWorkflow = (workflowId: string): void => {
    if (confirm('Are you sure you want to delete this workflow?')) {
      const updatedWorkflows = savedWorkflows.filter(w => w.id !== workflowId);
      localStorage.setItem('savedWorkflows', JSON.stringify(updatedWorkflows));
      setSavedWorkflows(updatedWorkflows);
      updatePresetsCategory(updatedWorkflows);
    }
  };

  return (
    <div className="node-palette">
      <div className="palette-header">
        <h3>Node</h3>
        <div className="search-container">
          <input
            type="text"
            className="search-input"
            placeholder={t('nodePalette.searchPlaceholder')}
            value={searchKeyword}
            onChange={handleSearchChange}
          />
          {searchKeyword && (
            <button
              className="clear-search"
              onClick={() => handleSearchChange({ target: { value: '' } })}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          )}
        </div>
      </div>
      <div className="palette-content">
        {loading ? (
          <div className="loading">Loading...</div>
        ) : showSearchResults && searchKeyword ? (
          
          <div className="search-results">
            <h4>Search Results: {searchResults.length}</h4>
            {searchResults.length > 0 ? (
              searchResults.map((node) => (
                <div
                  key={node.id}
                  className="palette-node search-result-node"
                  draggable
                  onDragStart={(event) => onDragStart(event, node)}
                >
                  <div className="node-icon">
                    {node.categoryIcon}
                  </div>
                  <div className="node-info">
                    <div className="node-label">{t(node.label)}</div>
                    <div className="node-description">{t(node.description)}</div>
                    <div className="node-category">{t(node.categoryName)}</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="no-results">
                <p>No matching nodes found</p>
              </div>
            )}
          </div>
        ) : (
          
          nodeCategories.length > 0 ? (
            nodeCategories.map((category) => (
              <div key={category.id} className="palette-category">
                <div className="category-header" 
                  onClick={() => toggleCategory(category.id)}
                >
                  <span className="category-icon">{category.icon}</span>
                  <span className="category-name">{category.name}</span>
                  <span className={`category-toggle ${expandedCategories.includes(category.id) ? 'expanded' : ''}`}>
                    {expandedCategories.includes(category.id) ? 
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="6 9 12 15 18 9"/></svg> : 
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 6 15 12 9 18"/></svg>}
                  </span>
                </div>
                
                {expandedCategories.includes(category.id) && (
                  <div className="category-nodes">
                    {category.nodes.map((node) => (
                      <div
                    key={node.id}
                    className={`palette-node ${node.type === 'preset' ? 'preset-node' : ''}`}
                    draggable={node.type !== 'preset'}
                    onDragStart={(event) => onDragStart(event, node)}
                    onClick={() => node.type === 'preset' && handlePresetClick(node)}
                  >
                    <div className="node-icon">
                      {node.type === 'preset' ? NODE_ICONS.preset : category.icon}
                    </div>
                    <div className="node-info">
                      <div className="node-label">{t(node.label)}</div>
                      <div className="node-description">{t(node.description)}</div>
                    </div>
                    {node.type === 'preset' && (
                      <div className="preset-actions">
                        <button 
                          className="delete-preset-btn" 
                          onClick={(e) => {
                            e.stopPropagation();
                            node.workflowData && handleDeleteWorkflow(node.workflowData.id);
                          }}
                          title="删除预设"
                        >
                          ✕
                        </button>
                      </div>
                    )}
                  </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          ) : (
            <div className="empty-palette">
              <p>No node data loaded</p>
            </div>
          )
        )}
      </div>
    </div>
  );
}

export default React.memo(NodePalette as React.FC<NodePaletteProps>);