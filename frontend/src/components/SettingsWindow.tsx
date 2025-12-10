import React, { useState, useEffect } from 'react';
import './SettingsWindow.css';
import { useI18n } from '../contexts/I18nContext';
import { SettingsIcon } from './Icons'; // 导入设置图标组件

interface SettingsWindowProps {
  isOpen: boolean;
  onClose: () => void;
}

const SettingsWindow: React.FC<SettingsWindowProps> = ({ isOpen, onClose }) => {
  // 使用i18n上下文
  const { currentLanguage, setCurrentLanguage, t } = useI18n();
  
  const [selectedMenu, setSelectedMenu] = useState('general');
  const [selectedTheme] = useState('dark'); // 只保留暗色主题，不需要setter
  const [selectedLanguage, setSelectedLanguage] = useState<string>(currentLanguage);
  
  // 当上下文语言变化时，更新本地状态
  useEffect(() => {
    setSelectedLanguage(currentLanguage);
  }, [currentLanguage]);

  if (!isOpen) return null;

  // 主题切换逻辑已简化，因为现在只有暗色主题
  const handleThemeChange = (_e: React.ChangeEvent<HTMLSelectElement>) => {
    // 只保留暗色主题，不需要实际切换
    console.log('当前只有暗色主题');
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const language = e.target.value;
    setSelectedLanguage(language);
    setCurrentLanguage(language);
    console.log(`切换到语言: ${language}`);
  };

  return (
    <div className="settings-overlay" onClick={onClose}>
      <div className="settings-window" onClick={(e) => e.stopPropagation()}>
        <div className="settings-header">
          <h2>{t('settings.title')}</h2>
          <button className="settings-close-btn" onClick={onClose}>
            &times;
          </button>
        </div>
        
        <div className="settings-content">
          <div className="settings-menu">
            <div className="menu-group">
              <button 
                className={`menu-item ${selectedMenu === 'general' ? 'active' : ''}`}
                onClick={() => setSelectedMenu('general')}
              >
                <span className="menu-icon"><SettingsIcon size={18} /></span>
                {t('settings.general')}
              </button>
            </div>
            
            <div className="menu-group">
              <button 
                className={`menu-item ${selectedMenu === 'about' ? 'active' : ''}`}
                onClick={() => setSelectedMenu('about')}
              >
                <span className="menu-icon">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="16" x2="12" y2="12" />
                    <line x1="12" y1="8" x2="12.01" y2="8" />
                  </svg>
                </span>
                {t('settings.about')}
              </button>
            </div>
          </div>
          
          <div className="settings-panel">
            {selectedMenu === 'general' && (
              <div className="general-settings">
                <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"></path></svg> {t('settings.general')}</h3>
                
                <div className="setting-item">
                  <div className="setting-label">
                    <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg> {t('settings.theme')}</span>
                    <span className="setting-description">{t('settings.theme.select')}</span>
                  </div>
                  <div className="setting-control">
                    <select 
                      value={selectedTheme} 
                      onChange={handleThemeChange}
                      className="settings-select"
                      disabled
                    >
                      <option value="dark">{t('settings.theme.dark')}</option>
                    </select>
                  </div>
                </div>
                
                <div className="setting-item">
                  <div className="setting-label">
                    <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 7V4h16v3"></path><path d="M9 20h6"></path><path d="M12 4v16"></path><path d="M12 16h.01"></path></svg> {t('settings.language')}</span>
                    <span className="setting-description">{t('settings.language.select')}</span>
                  </div>
                  <div className="setting-control">
                    <select 
                      value={selectedLanguage} 
                      onChange={handleLanguageChange}
                      className="settings-select"
                    >
                      <option value="zh-CN">{t('settings.language.zh-CN')}</option>
                      <option value="en-US">{t('settings.language.en-US')}</option>
                    </select>
                  </div>
                </div>
                
                <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06a1.65 1.65 0 00.33-1.82 1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06a1.65 1.65 0 001.82.33H9a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06a1.65 1.65 0 00-.33 1.82V9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"></path></svg> {t('settings.preferences')}</h3>
                
                <div className="setting-item">
                  <div className="setting-label">
                    <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg> {t('settings.editor.settings')}</span>
                    <span className="setting-description">{t('settings.editor.description')}</span>
                  </div>
                  <div className="setting-control">
                    <button className="go-to-settings-btn">{t('settings.editor.goToSettings')}</button>
                  </div>
                </div>
                
                <div className="setting-item">
                  <div className="setting-label">
                    <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3H6a3 3 0 0 0-3 3 3 3 0 0 0 3 3 3 3 0 0 0 3-3V6a3 3 0 0 0-3-3 3 3 0 0 0-3 3 3 3 0 0 0 3 3h12a3 3 0 0 0 3-3 3 3 0 0 0-3-3z"></path></svg> {t('settings.shortcutSettings')}</span>
                    <span className="setting-description">{t('settings.shortcutSettings.description')}</span>
                  </div>
                  <div className="setting-control">
                    <button className="go-to-settings-btn">{t('settings.shortcutSettings.goTo')}</button>
                  </div>
                </div>
                
                <div className="setting-item">
                  <div className="setting-label">
                    <span><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg> {t('settings.importConfig')}</span>
                    <span className="setting-description">{t('settings.importConfig.description')}</span>
                  </div>
                  <div className="setting-control">
                    <button className="go-to-settings-btn">{t('settings.importConfig.import')}</button>
                  </div>
                </div>
              </div>
            )}
            
            {/* 其他菜单项的内容可以在这里添加 */}
            {selectedMenu === 'about' && (
              <div className="about-cognot">
                <h3><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg> {t('settings.about.title')}</h3>
                <p>{t('settings.about.description')}</p>
                <div className="github-link">
                  <a href="https://github.com/CognotEngine/Cognot" target="_blank" rel="noopener noreferrer" className="btn-github">
                    <span className="github-icon">
                      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path>
                      </svg>
                    </span>
                    <span className="github-url">github.com/CognotEngine/Cognot</span>
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsWindow;
