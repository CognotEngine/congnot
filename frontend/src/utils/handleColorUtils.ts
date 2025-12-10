// 根据数据类型获取连接点颜色
export const getHandleColorByDataType = (dataType: string): string => {
  switch (dataType) {
    case 'model':
      return '#E6E6FA'; // 扩散模型 - 淡紫色 (Lavender)
    case 'clip':
      return '#FFFF00'; // CLIP 模型 - 黄色 (Yellow)
    case 'vae':
      return '#FF007F'; // VAE模型 - 玫瑰红 (Rose)
    case 'prompt':
      return '#FFA500'; // 提示词信息 - 橙色 (Orange)
    case 'latent':
      return '#FFC0CB'; // 潜在图像 - 粉色 (Pink)
    case 'image':
      return '#0000FF'; // 像素图像 - 蓝色 (Blue)
    case 'mask':
      return '#008000'; // 遮罩数据 - 绿色 (Green)
    case 'number':
      return '#90EE90'; // 数字 - 浅绿色 (Light Green)
    case 'string':
      return '#FFC300'; // 字符串数据类型 - 黄色
    case 'boolean':
      return '#888888'; // 布尔数据类型 - 灰色
    default:
      return '#888888'; // 默认颜色 - 灰色
  }
};

// 根据数据类型获取线条颜色
export const getEdgeColorByDataType = (dataType: string): string => {
  return getHandleColorByDataType(dataType);
};