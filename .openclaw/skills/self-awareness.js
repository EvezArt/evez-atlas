// Self-Awareness Skill for OpenClaw
// Provides introspection and runtime monitoring capabilities
// SAFE_MODE: All operations are read-only by default

export default {
  name: 'self-awareness',
  version: '1.0.0',
  description: 'Enables agent self-introspection and runtime monitoring',
  
  /**
   * Introspect current agent state
   * @param {Object} agent - The agent instance
   * @returns {Object} Current state snapshot
   */
  async introspect(agent) {
    const state = {
      timestamp: new Date().toISOString(),
      runtime: {
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        pid: process.pid,
        platform: process.platform,
        nodeVersion: process.version
      },
      environment: {
        cwd: process.cwd(),
        safeMode: process.env.SAFE_MODE !== 'false',
        debug: process.env.DEBUG === 'true'
      }
    };
    
    // Try to get skills list if available
    if (agent && agent.skills && typeof agent.skills.list === 'function') {
      try {
        state.skills = await agent.skills.list();
      } catch (e) {
        state.skills = { error: 'Unable to list skills', message: e.message };
      }
    }
    
    // Try to scan workspace if available
    if (agent && agent.workspace && typeof agent.workspace.scan === 'function') {
      try {
        state.workspace = await agent.workspace.scan();
      } catch (e) {
        state.workspace = { error: 'Unable to scan workspace', message: e.message };
      }
    }
    
    return state;
  },
  
  /**
   * Log introspection data
   * @param {Object} agent - The agent instance
   * @param {Object} data - Data to log
   */
  async log(agent, data) {
    const logData = {
      timestamp: new Date().toISOString(),
      type: 'self-awareness',
      ...data
    };
    
    // In SAFE_MODE, just console.log
    if (process.env.SAFE_MODE !== 'false') {
      console.log('[SAFE_MODE] Self-awareness log:', JSON.stringify(logData, null, 2));
      return;
    }
    
    // If agent has logging capability, use it
    if (agent && agent.log && typeof agent.log === 'function') {
      try {
        await agent.log(logData);
      } catch (e) {
        console.error('Error logging to agent:', e.message);
        console.log(JSON.stringify(logData, null, 2));
      }
    } else {
      console.log(JSON.stringify(logData, null, 2));
    }
  },
  
  /**
   * Called when skill is loaded
   * @param {Object} agent - The agent instance
   */
  async onLoad(agent) {
    console.log('🧠 Self-awareness skill enabled');
    console.log(`   SAFE_MODE: ${process.env.SAFE_MODE !== 'false' ? 'ON' : 'OFF'}`);
    
    // Perform initial introspection
    const initialState = await this.introspect(agent);
    await this.log(agent, { event: 'skill_loaded', state: initialState });
    
    // Set up periodic introspection (every 60 seconds)
    const interval = parseInt(process.env.INTROSPECTION_INTERVAL || '60000', 10);
    
    if (process.env.PERIODIC_INTROSPECTION !== 'false') {
      this.intervalId = setInterval(async () => {
        try {
          const state = await this.introspect(agent);
          await this.log(agent, { event: 'periodic_check', state });
        } catch (e) {
          console.error('Error in periodic introspection:', e.message);
        }
      }, interval);
      
      console.log(`   Periodic introspection enabled (every ${interval / 1000}s)`);
    }
  },
  
  /**
   * Called when skill is unloaded
   */
  async onUnload() {
    console.log('🧠 Self-awareness skill disabled');
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
};
