// ChatGPT Integration Skill for OpenClaw
// Provides OpenAI ChatGPT API integration
// SAFE_MODE: API calls are logged but not executed by default

export default {
  name: 'chatgpt-integration',
  version: '1.0.0',
  description: 'Enables ChatGPT API integration for enhanced reasoning',
  
  /**
   * Initialize OpenAI client
   * @returns {Object|null} OpenAI client or null if not available
   */
  initClient() {
    // Check if we have the API key
    if (!process.env.OPENAI_API_KEY) {
      console.warn('[ChatGPT] OPENAI_API_KEY not found in environment');
      return null;
    }
    
    // Try to load OpenAI package
    try {
      // Note: This requires 'openai' package to be installed
      const OpenAI = require('openai');
      return new OpenAI({
        apiKey: process.env.OPENAI_API_KEY
      });
    } catch (e) {
      console.warn('[ChatGPT] OpenAI package not available:', e.message);
      console.warn('[ChatGPT] Install with: npm install openai');
      return null;
    }
  },
  
  /**
   * Query ChatGPT with a prompt
   * @param {String} prompt - The prompt to send
   * @param {Object} options - Additional options
   * @returns {String} Response from ChatGPT
   */
  async query(prompt, options = {}) {
    // In SAFE_MODE, don't make actual API calls
    if (process.env.SAFE_MODE !== 'false') {
      console.log('[SAFE_MODE] ChatGPT query logged but not executed:');
      console.log('Prompt:', prompt.substring(0, 100) + '...');
      return '[SAFE_MODE] ChatGPT response would appear here';
    }
    
    const client = this.initClient();
    if (!client) {
      return '[ERROR] ChatGPT client not available. Check API key and package installation.';
    }
    
    try {
      const response = await client.chat.completions.create({
        model: options.model || 'gpt-4-turbo-preview',
        messages: [
          {
            role: 'system',
            content: options.systemPrompt || 'You are a helpful AI assistant integrated with OpenClaw.'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: options.temperature || 0.7,
        max_tokens: options.maxTokens || 1000
      });
      
      return response.choices[0].message.content;
    } catch (e) {
      console.error('[ChatGPT] Error querying API:', e.message);
      return `[ERROR] ${e.message}`;
    }
  },
  
  /**
   * Analyze text with ChatGPT
   * @param {String} text - Text to analyze
   * @param {String} analysisType - Type of analysis
   * @returns {Object} Analysis results
   */
  async analyze(text, analysisType = 'general') {
    const prompts = {
      general: `Analyze the following text and provide key insights:\n\n${text}`,
      sentiment: `Analyze the sentiment of the following text (positive/negative/neutral):\n\n${text}`,
      summary: `Provide a concise summary of the following text:\n\n${text}`,
      improvements: `Suggest improvements for the following text:\n\n${text}`
    };
    
    const prompt = prompts[analysisType] || prompts.general;
    const response = await this.query(prompt, {
      systemPrompt: 'You are an expert text analyst. Provide clear, actionable insights.'
    });
    
    return {
      type: analysisType,
      input: text.substring(0, 100) + '...',
      analysis: response,
      timestamp: new Date().toISOString()
    };
  },
  
  /**
   * Get code suggestions from ChatGPT
   * @param {String} code - Code to analyze
   * @param {String} language - Programming language
   * @returns {Object} Code suggestions
   */
  async suggestCodeImprovements(code, language = 'javascript') {
    const prompt = `Review the following ${language} code and suggest improvements for:
    1. Performance
    2. Readability
    3. Best practices
    4. Potential bugs
    
    Code:
    \`\`\`${language}
    ${code}
    \`\`\``;
    
    const response = await this.query(prompt, {
      systemPrompt: 'You are an expert code reviewer. Provide specific, actionable suggestions.',
      maxTokens: 2000
    });
    
    return {
      language,
      suggestions: response,
      timestamp: new Date().toISOString()
    };
  },
  
  /**
   * Called when skill is loaded
   * @param {Object} agent - The agent instance
   */
  async onLoad(agent) {
    console.log('💬 ChatGPT integration enabled');
    console.log(`   SAFE_MODE: ${process.env.SAFE_MODE !== 'false' ? 'ON (no API calls)' : 'OFF (API calls active)'}`);
    console.log(`   API Key: ${process.env.OPENAI_API_KEY ? '✓ Configured' : '✗ Missing'}`);
    
    // Test initialization
    const client = this.initClient();
    if (client) {
      console.log('   OpenAI client: ✓ Ready');
    } else {
      console.log('   OpenAI client: ✗ Not available');
    }
    
    // Make client available to agent
    if (agent) {
      agent.chatgpt = {
        query: this.query.bind(this),
        analyze: this.analyze.bind(this),
        suggestCodeImprovements: this.suggestCodeImprovements.bind(this)
      };
    }
  },
  
  /**
   * Called when skill is unloaded
   */
  async onUnload() {
    console.log('💬 ChatGPT integration disabled');
  }
};
