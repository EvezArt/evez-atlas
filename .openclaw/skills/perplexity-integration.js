// Perplexity Integration Skill for OpenClaw
// Provides Perplexity API integration for research and fact-checking
// SAFE_MODE: API calls are logged but not executed by default

export default {
  name: 'perplexity-integration',
  version: '1.0.0',
  description: 'Enables Perplexity API integration for research and fact-checking',
  
  /**
   * Initialize Perplexity client
   * @returns {Object|null} Client configuration or null if not available
   */
  initClient() {
    // Check if we have the API key
    if (!process.env.PERPLEXITY_API_KEY) {
      console.warn('[Perplexity] PERPLEXITY_API_KEY not found in environment');
      return null;
    }
    
    return {
      apiKey: process.env.PERPLEXITY_API_KEY,
      baseURL: 'https://api.perplexity.ai'
    };
  },
  
  /**
   * Query Perplexity API
   * @param {String} query - The search query
   * @param {Object} options - Additional options
   * @returns {Object} Response from Perplexity
   */
  async search(query, options = {}) {
    // In SAFE_MODE, don't make actual API calls
    if (process.env.SAFE_MODE !== 'false') {
      console.log('[SAFE_MODE] Perplexity search logged but not executed:');
      console.log('Query:', query);
      return {
        safeMode: true,
        query,
        answer: '[SAFE_MODE] Search results would appear here',
        citations: []
      };
    }
    
    const client = this.initClient();
    if (!client) {
      return {
        error: 'Perplexity client not available. Check API key configuration.',
        query
      };
    }
    
    try {
      // Perplexity uses OpenAI-compatible API
      const fetch = require('node-fetch');
      
      const response = await fetch(`${client.baseURL}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${client.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: options.model || 'sonar-medium-online',
          messages: [
            {
              role: 'system',
              content: 'Be precise and concise. Provide citations when possible.'
            },
            {
              role: 'user',
              content: query
            }
          ],
          temperature: options.temperature || 0.2,
          max_tokens: options.maxTokens || 1000
        })
      });
      
      if (!response.ok) {
        throw new Error(`API returned ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      return {
        query,
        answer: data.choices[0].message.content,
        model: data.model,
        citations: data.citations || [],
        timestamp: new Date().toISOString()
      };
    } catch (e) {
      console.error('[Perplexity] Error querying API:', e.message);
      return {
        error: e.message,
        query
      };
    }
  },
  
  /**
   * Fact-check a statement
   * @param {String} statement - Statement to fact-check
   * @returns {Object} Fact-check results
   */
  async factCheck(statement) {
    const query = `Fact-check the following statement and provide evidence:\n\n"${statement}"\n\nIs this accurate? Provide sources.`;
    const result = await this.search(query, {
      model: 'sonar-medium-online',
      temperature: 0.1  // Lower temperature for fact-checking
    });
    
    return {
      statement,
      factCheck: result.answer,
      citations: result.citations,
      confidence: this.extractConfidence(result.answer),
      timestamp: result.timestamp
    };
  },
  
  /**
   * Extract confidence level from response
   * @param {String} answer - The response text
   * @returns {String} Confidence level
   */
  extractConfidence(answer) {
    const lower = answer.toLowerCase();
    if (lower.includes('definitely') || lower.includes('certainly')) return 'high';
    if (lower.includes('likely') || lower.includes('probably')) return 'medium';
    if (lower.includes('unclear') || lower.includes('uncertain')) return 'low';
    return 'unknown';
  },
  
  /**
   * Research a topic
   * @param {String} topic - Topic to research
   * @param {Object} options - Research options
   * @returns {Object} Research results
   */
  async research(topic, options = {}) {
    const query = options.detailed
      ? `Provide a comprehensive overview of: ${topic}. Include recent developments, key concepts, and important sources.`
      : `Provide a concise overview of: ${topic}`;
    
    const result = await this.search(query, {
      model: options.model || 'sonar-medium-online',
      maxTokens: options.detailed ? 2000 : 1000
    });
    
    return {
      topic,
      overview: result.answer,
      citations: result.citations,
      detailed: options.detailed || false,
      timestamp: result.timestamp
    };
  },
  
  /**
   * Called when skill is loaded
   * @param {Object} agent - The agent instance
   */
  async onLoad(agent) {
    console.log('🔍 Perplexity integration enabled');
    console.log(`   SAFE_MODE: ${process.env.SAFE_MODE !== 'false' ? 'ON (no API calls)' : 'OFF (API calls active)'}`);
    console.log(`   API Key: ${process.env.PERPLEXITY_API_KEY ? '✓ Configured' : '✗ Missing'}`);
    
    // Test initialization
    const client = this.initClient();
    if (client) {
      console.log('   Perplexity client: ✓ Ready');
    } else {
      console.log('   Perplexity client: ✗ Not available');
    }
    
    // Make methods available to agent
    if (agent) {
      agent.perplexity = {
        search: this.search.bind(this),
        factCheck: this.factCheck.bind(this),
        research: this.research.bind(this)
      };
    }
  },
  
  /**
   * Called when skill is unloaded
   */
  async onUnload() {
    console.log('🔍 Perplexity integration disabled');
  }
};
