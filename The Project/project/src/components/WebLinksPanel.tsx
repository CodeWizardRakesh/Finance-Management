import React from 'react';
import { ExternalLink, Globe } from 'lucide-react';

interface WebLinksPanelProps {
  webLinks: string;
}

const WebLinksPanel: React.FC<WebLinksPanelProps> = ({ webLinks }) => {
  const parseLinks = (linksString: string) => {
    if (!linksString.trim()) return [];
    
    const linkRegex = /- \[([^\]]+)\]\(([^)]+)\)/g;
    const links: { title: string; url: string }[] = [];
    let match;
    
    while ((match = linkRegex.exec(linksString)) !== null) {
      links.push({
        title: match[1],
        url: match[2],
      });
    }
    
    return links;
  };

  const links = parseLinks(webLinks);

  if (links.length === 0) {
    return (
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <div className="flex items-center space-x-2 mb-4">
          <Globe size={20} className="text-purple-500" />
          <h3 className="text-lg font-semibold text-white">Web Resources</h3>
        </div>
        <div className="text-center py-8">
          <Globe size={32} className="text-gray-600 mx-auto mb-3" />
          <p className="text-gray-400 text-sm">
            No web resources available for this query
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      <div className="flex items-center space-x-2 mb-4">
        <Globe size={20} className="text-purple-500" />
        <h3 className="text-lg font-semibold text-white">Web Resources</h3>
      </div>
      
      <div className="space-y-3">
        {links.map((link, index) => (
          <a
            key={index}
            href={link.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between p-3 bg-gray-800 rounded-lg border border-gray-700 hover:border-purple-500 hover:bg-gray-750 transition-all duration-200 group"
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white group-hover:text-purple-300 transition-colors">
                {link.title}
              </p>
              <p className="text-xs text-gray-400 truncate mt-1">
                {new URL(link.url).hostname}
              </p>
            </div>
            <ExternalLink size={16} className="text-gray-400 group-hover:text-purple-400 transition-colors ml-3 flex-shrink-0" />
          </a>
        ))}
      </div>
    </div>
  );
};

export default WebLinksPanel;