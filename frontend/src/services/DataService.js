/**
 * 数据服务 - 负责加载和处理医学知识图谱数据
 */

// 加载所有数据源
export async function loadAllData() {
  try {
    const [emrData, textbookData, paperData, guidelineData] = await Promise.all([
      loadEmrData(),
      loadTextbookData(),
      loadPaperData(),
      loadGuidelineData()
    ]);
    
    return [...emrData, ...textbookData, ...paperData, ...guidelineData];
  } catch (error) {
    console.error('加载数据失败:', error);
    return [];
  }
}

// 加载电子病历数据
export async function loadEmrData() {
  try {
    const response = await fetch('./data/json/emr_data.json');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('加载电子病历数据失败:', error);
    return [];
  }
}

// 加载教材数据
export async function loadTextbookData() {
  try {
    const response = await fetch('./data/json/textbook_data.json');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('加载教材数据失败:', error);
    return [];
  }
}

// 加载论文数据
export async function loadPaperData() {
  try {
    const response = await fetch('./data/json/paper_data.json');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('加载论文数据失败:', error);
    return [];
  }
}

// 加载临床指南数据
export async function loadGuidelineData() {
  try {
    const response = await fetch('./data/json/guideline_data.json');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('加载临床指南数据失败:', error);
    return [];
  }
}

// 搜索数据
export function searchData(items, query) {
  if (!query || !items || items.length === 0) {
    return items;
  }
  
  const lowerQuery = query.toLowerCase();
  
  return items.filter(item => {
    // 标题匹配
    if (item.title && item.title.toLowerCase().includes(lowerQuery)) {
      return true;
    }
    
    // 关键词匹配
    if (item.keywords && item.keywords.some(k => k.toLowerCase().includes(lowerQuery))) {
      return true;
    }
    
    // 摘要/总结匹配
    if ((item.abstract && item.abstract.toLowerCase().includes(lowerQuery)) || 
        (item.summary && item.summary.toLowerCase().includes(lowerQuery))) {
      return true;
    }
    
    // 作者匹配
    if (item.authors && item.authors.some(a => a.toLowerCase().includes(lowerQuery))) {
      return true;
    }
    
    // 教材章节匹配
    if (item.sections && item.sections.some(s => 
      (s.title && s.title.toLowerCase().includes(lowerQuery)) || 
      (s.content && s.content.toLowerCase().includes(lowerQuery))
    )) {
      return true;
    }
    
    // 临床指南建议匹配
    if (item.recommendations && item.recommendations.length > 0) {
      // 检查recommendations是否为字符串数组还是对象数组
      if (typeof item.recommendations[0] === 'string') {
        // 字符串数组情况
        if (item.recommendations.some(r => r.toLowerCase().includes(lowerQuery))) {
          return true;
        }
      } else if (typeof item.recommendations[0] === 'object') {
        // 对象数组情况 - 可能有section和content结构
        for (const rec of item.recommendations) {
          if (rec.section && rec.section.toLowerCase().includes(lowerQuery)) {
            return true;
          }
          if (rec.content && Array.isArray(rec.content)) {
            if (rec.content.some(c => c.toLowerCase().includes(lowerQuery))) {
              return true;
            }
          }
        }
      }
    }
    
    return false;
  });
} 