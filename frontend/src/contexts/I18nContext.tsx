import React, { createContext, useState, useContext, ReactNode, useEffect } from 'react';
import { initLanguage, setLanguage, resources } from '../utils/i18n';

// 定义上下文类型
interface I18nContextType {
  currentLanguage: string;
  setCurrentLanguage: (language: string) => void;
  t: (key: string, params?: { [key: string]: string | number }) => string;
  availableLanguages: string[];
}

// 创建上下文
const I18nContext = createContext<I18nContextType | undefined>(undefined);

// 提供者组件类型
interface I18nProviderProps {
  children: ReactNode;
}

// 提供者组件
export const I18nProvider: React.FC<I18nProviderProps> = ({ children }) => {
  const [language, setLanguageState] = useState<string>('en-US');
  
  // 初始化语言
  useEffect(() => {
    initLanguage();
    // 从i18n.ts获取当前语言
    const savedLanguage = localStorage.getItem('language');
    const browserLanguage = navigator.language || 'en-US';
    
    if (savedLanguage && resources[savedLanguage]) {
      setLanguageState(savedLanguage);
    } else if (resources[browserLanguage]) {
      setLanguageState(browserLanguage);
    } else if (resources[browserLanguage.split('-')[0]]) {
      // 尝试匹配语言前缀，比如'en'匹配'en-US'
      setLanguageState(browserLanguage.split('-')[0]);
    }
  }, []);
  
  // 设置当前语言
  const setCurrentLanguage = (newLanguage: string) => {
    if (resources[newLanguage]) {
      setLanguage(newLanguage);
      setLanguageState(newLanguage);
    }
  };
  
  // 自定义翻译函数，使用当前语言状态
  const t = (key: string, params?: { [key: string]: string | number }): string => {
    let text = resources[language]?.[key] || resources['en-US']?.[key] || key;
    
    // 替换参数
    if (params) {
      Object.entries(params).forEach(([paramKey, paramValue]) => {
        text = text.replace(`{{${paramKey}}}`, String(paramValue));
      });
    }
    
    return text;
  };
  
  // 获取可用语言列表
  const availableLanguages = Object.keys(resources);
  
  return (
    <I18nContext.Provider value={{ currentLanguage: language, setCurrentLanguage, t, availableLanguages }}>
      {children}
    </I18nContext.Provider>
  );
};

// 自定义钩子
export const useI18n = (): I18nContextType => {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error('useI18n must be used within an I18nProvider');
  }
  return context;
};