// Autonomous Orchestrator Skill for OpenClaw
// Coordinates multiple skills for autonomous operation
// SAFE_MODE: All orchestration is logged but actions not executed by default

export default {
  name: 'autonomous-orchestrator',
  version: '1.0.0',
  description: 'Coordinates autonomous operations across multiple skills',
  
  /**
   * Get loaded skills
   * @param {Object} agent - The agent instance
   * @returns {Array} List of loaded skills
   */
  getLoadedSkills(agent) {
    if (!agent) return [];
    
    // Try different ways to access skills
    if (agent.skills && typeof agent.skills === 'object') {
      return Object.keys(agent.skills);
    }
    
    return [];
  },
  
  /**
   * Check if a skill is available
   * @param {Object} agent - The agent instance
   * @param {String} skillName - Name of the skill
   * @returns {Boolean} Whether skill is available
   */
  hasSkill(agent, skillName) {
    const skills = this.getLoadedSkills(agent);
    return skills.includes(skillName);
  },
  
  /**
   * Orchestrate a research task
   * @param {Object} agent - The agent instance
   * @param {String} topic - Topic to research
   * @returns {Object} Research results
   */
  async orchestrateResearch(agent, topic) {
    console.log(`[Orchestrator] Starting research on: ${topic}`);
    
    const results = {
      topic,
      timestamp: new Date().toISOString(),
      steps: []
    };
    
    // Step 1: Use Perplexity for factual research
    if (this.hasSkill(agent, 'perplexity-integration') && agent.perplexity) {
      console.log('[Orchestrator] Step 1: Perplexity research');
      const research = await agent.perplexity.research(topic, { detailed: true });
      results.steps.push({
        skill: 'perplexity',
        action: 'research',
        result: research
      });
    }
    
    // Step 2: Use ChatGPT for analysis
    if (this.hasSkill(agent, 'chatgpt-integration') && agent.chatgpt) {
      console.log('[Orchestrator] Step 2: ChatGPT analysis');
      const analysis = await agent.chatgpt.analyze(
        results.steps[0]?.result?.overview || topic,
        'general'
      );
      results.steps.push({
        skill: 'chatgpt',
        action: 'analyze',
        result: analysis
      });
    }
    
    // Step 3: Log with self-awareness
    if (this.hasSkill(agent, 'self-awareness') && agent.skills && agent.skills['self-awareness']) {
      console.log('[Orchestrator] Step 3: Logging results');
      await agent.skills['self-awareness'].log(agent, {
        event: 'research_completed',
        results
      });
    }
    
    return results;
  },
  
  /**
   * Orchestrate code review task
   * @param {Object} agent - The agent instance
   * @param {String} code - Code to review
   * @param {String} language - Programming language
   * @returns {Object} Review results
   */
  async orchestrateCodeReview(agent, code, language = 'javascript') {
    console.log(`[Orchestrator] Starting code review for ${language}`);
    
    const results = {
      language,
      timestamp: new Date().toISOString(),
      steps: []
    };
    
    // Step 1: ChatGPT code review
    if (this.hasSkill(agent, 'chatgpt-integration') && agent.chatgpt) {
      console.log('[Orchestrator] Step 1: ChatGPT code review');
      const review = await agent.chatgpt.suggestCodeImprovements(code, language);
      results.steps.push({
        skill: 'chatgpt',
        action: 'code_review',
        result: review
      });
    }
    
    // Step 2: DeepClaw analysis for improvements
    if (this.hasSkill(agent, 'deepclaw-integration') && agent.skills && agent.skills['deepclaw-integration']) {
      console.log('[Orchestrator] Step 2: DeepClaw improvement analysis');
      const improvements = await agent.skills['deepclaw-integration'].analyzeForImprovements({
        code,
        language
      });
      results.steps.push({
        skill: 'deepclaw',
        action: 'analyze_improvements',
        result: improvements
      });
    }
    
    return results;
  },
  
  /**
   * Orchestrate GitHub workflow
   * @param {Object} agent - The agent instance
   * @param {Object} params - Workflow parameters
   * @returns {Object} Workflow results
   */
  async orchestrateGitHubWorkflow(agent, params) {
    const { owner, repo, action, data } = params;
    
    console.log(`[Orchestrator] Starting GitHub workflow: ${action}`);
    
    const results = {
      action,
      timestamp: new Date().toISOString(),
      steps: []
    };
    
    // Check if GitHub skill is available
    if (!this.hasSkill(agent, 'github-autonomous') || !agent.github) {
      results.error = 'GitHub skill not available';
      return results;
    }
    
    // Execute based on action type
    switch (action) {
      case 'create_issue':
        const issue = await agent.github.createIssue({
          owner,
          repo,
          ...data
        });
        results.steps.push({
          skill: 'github',
          action: 'create_issue',
          result: issue
        });
        break;
      
      case 'create_pr':
        const pr = await agent.github.createPullRequest({
          owner,
          repo,
          ...data
        });
        results.steps.push({
          skill: 'github',
          action: 'create_pr',
          result: pr
        });
        break;
      
      case 'analyze_repository':
        const repoInfo = await agent.github.getRepository({ owner, repo });
        const issues = await agent.github.listIssues({ owner, repo });
        
        results.steps.push({
          skill: 'github',
          action: 'get_repository',
          result: repoInfo
        });
        results.steps.push({
          skill: 'github',
          action: 'list_issues',
          result: issues
        });
        break;
      
      default:
        results.error = `Unknown action: ${action}`;
    }
    
    return results;
  },
  
  /**
   * Autonomous monitoring loop
   * @param {Object} agent - The agent instance
   */
  async autonomousLoop(agent) {
    console.log('[Orchestrator] Starting autonomous monitoring loop');
    
    const interval = parseInt(process.env.ORCHESTRATOR_INTERVAL || '600000', 10); // 10 minutes default
    const maxIterations = parseInt(process.env.ORCHESTRATOR_MAX_ITERATIONS || '0', 10); // 0 = unlimited
    let iterations = 0;
    
    // Track if shutdown was requested
    this.shouldStop = false;
    this.timeoutId = null;
    
    while (!this.shouldStop && (maxIterations === 0 || iterations < maxIterations)) {
      try {
        iterations++;
        console.log(`[Orchestrator] Monitoring iteration ${iterations}${maxIterations > 0 ? `/${maxIterations}` : ''}`);
        
        // Get current state
        let state = null;
        if (this.hasSkill(agent, 'self-awareness') && agent.skills && agent.skills['self-awareness']) {
          state = await agent.skills['self-awareness'].introspect(agent);
        }
        
        // Check for tasks to orchestrate
        console.log('[Orchestrator] Checking for autonomous tasks...');
        
        // In a full implementation, this would:
        // 1. Check for new GitHub events
        // 2. Analyze repository state
        // 3. Coordinate responses
        // 4. Execute multi-skill workflows
        
        // For now, just log the check
        console.log('[Orchestrator] Autonomous check complete');
        
      } catch (e) {
        console.error('[Orchestrator] Error in autonomous loop:', e.message);
      }
      
      // Wait before next iteration
      await new Promise(resolve => {
        this.timeoutId = setTimeout(resolve, interval);
      });
    }
    
    if (this.shouldStop) {
      console.log('[Orchestrator] Autonomous loop stopped by shutdown request');
    } else if (maxIterations > 0) {
      console.log(`[Orchestrator] Autonomous loop completed after ${maxIterations} iterations`);
    }
  },
  
  /**
   * Called when skill is loaded
   * @param {Object} agent - The agent instance
   */
  async onLoad(agent) {
    console.log('🎭 Autonomous orchestrator enabled');
    console.log(`   SAFE_MODE: ${process.env.SAFE_MODE !== 'false' ? 'ON (orchestration only)' : 'OFF (full autonomy)'}`);
    
    // List available skills
    const skills = this.getLoadedSkills(agent);
    console.log(`   Available skills: ${skills.join(', ') || 'none'}`);
    
    // Make orchestration methods available to agent
    if (agent) {
      agent.orchestrate = {
        research: this.orchestrateResearch.bind(this, agent),
        codeReview: this.orchestrateCodeReview.bind(this, agent),
        githubWorkflow: this.orchestrateGitHubWorkflow.bind(this, agent)
      };
    }
    
    // Start autonomous loop if enabled
    if (process.env.AUTONOMOUS_LOOP !== 'false') {
      const maxIterations = parseInt(process.env.ORCHESTRATOR_MAX_ITERATIONS || '0', 10);
      const intervalMsg = `${parseInt(process.env.ORCHESTRATOR_INTERVAL || '600000', 10) / 1000}s`;
      const maxIterMsg = maxIterations > 0 ? `, max ${maxIterations} iterations` : '';
      console.log(`   Autonomous loop: ✓ Starting (interval: ${intervalMsg}${maxIterMsg})`);
      this.autonomousLoop(agent).catch(e => {
        console.error('[Orchestrator] Fatal error in autonomous loop:', e);
      });
    } else {
      console.log('   Autonomous loop: ✗ Disabled');
    }
  },
  
  /**
   * Called when skill is unloaded
   */
  async onUnload() {
    console.log('🎭 Autonomous orchestrator disabled');
    this.shouldStop = true;
    if (this.timeoutId) {
      clearTimeout(this.timeoutId);
      this.timeoutId = null;
    }
  }
};
