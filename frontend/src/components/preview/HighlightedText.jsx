import React, { useMemo } from 'react';

const escapeRegExp = (string) => {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
};

const HighlightedText = ({ text, matchedSkills = [], missingSkills = [] }) => {
  // Memoize the regex and parts processing to prevent unnecessary re-renders on long texts
  const parts = useMemo(() => {
    if (!text) return [];

    // Extract raw skill strings
    const matchedNames = matchedSkills.map(s => (s.required_skill || s.skill || s.name || '').trim()).filter(Boolean);
    const missingNames = missingSkills.map(s => (s.skill || s.name || '').trim()).filter(Boolean);

    if (matchedNames.length === 0 && missingNames.length === 0) {
      return [{ text, type: 'normal' }];
    }

    // Sort by length descending to match longest phrases first (e.g., "Machine Learning" before "Learning")
    const allSkills = [
      ...matchedNames.map(name => ({ name, type: 'matched' })),
      ...missingNames.map(name => ({ name, type: 'missing' }))
    ].sort((a, b) => b.name.length - a.name.length);

    // Build a massive OR regex: (Skill A|Skill B|Skill C)
    const patternStr = allSkills.map(s => escapeRegExp(s.name)).join('|');
    // We use \b to ensure word boundary match, but some skills might contain special chars.
    // If it starts/ends with word char, use \b. It's safer to just split by the exact phrase ignoring case.
    // Since skills might not have word boundaries perfectly matching due to punctuation, 
    // we use a regex without \b but be careful of sub-word matching? 
    // Actually, \b is safer to prevent "React" matching "Reactive".
    // We'll wrap in \b but handle cases where skill starts with non-word.
    
    // A robust way to build regex for exact phrase matching with boundaries:
    const regex = new RegExp(`\\b(${patternStr})\\b`, 'gi');
    
    const resultParts = [];
    let lastIndex = 0;
    
    text.replace(regex, (match, p1, offset) => {
      // Push preceding normal text
      if (offset > lastIndex) {
        resultParts.push({ text: text.substring(lastIndex, offset), type: 'normal' });
      }
      
      // Determine type
      const lowerMatch = match.toLowerCase();
      let type = 'normal';
      
      if (matchedNames.some(s => s.toLowerCase() === lowerMatch)) {
        type = 'matched';
      } else if (missingNames.some(s => s.toLowerCase() === lowerMatch)) {
        type = 'missing';
      }
      
      resultParts.push({ text: match, type });
      lastIndex = offset + match.length;
      return match;
    });

    // Push remaining normal text
    if (lastIndex < text.length) {
      resultParts.push({ text: text.substring(lastIndex), type: 'normal' });
    }

    return resultParts;
  }, [text, matchedSkills, missingSkills]);

  return (
    <span style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
      {parts.map((part, i) => {
        if (part.type === 'matched') {
          return (
            <span
              key={i}
              style={{
                backgroundColor: 'rgba(34, 197, 94, 0.15)',
                border: '1px solid rgba(34, 197, 94, 0.4)',
                borderRadius: '4px',
                padding: '0 4px',
                margin: '0 2px',
                color: 'inherit'
              }}
              title="Matched Skill"
            >
              {part.text}
            </span>
          );
        } else if (part.type === 'missing') {
          return (
            <span
              key={i}
              style={{
                backgroundColor: 'rgba(249, 115, 22, 0.15)',
                border: '1px solid rgba(249, 115, 22, 0.4)',
                borderRadius: '4px',
                padding: '0 4px',
                margin: '0 2px',
                color: 'inherit'
              }}
              title="Missing Skill Requirement"
            >
              {part.text}
            </span>
          );
        }
        return <span key={i}>{part.text}</span>;
      })}
    </span>
  );
};

export default HighlightedText;
