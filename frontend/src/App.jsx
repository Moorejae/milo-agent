import React, { useState, useEffect, useRef } from 'react';
import {
  Bot,
  Terminal,
  BrainCircuit,
  Wrench,
  BarChart3,
  Settings,
  Send,
  Play,
  Pause,
  Plus,
  Search,
  CheckCircle2,
  AlertCircle,
  Clock,
  Cpu,
  Database,
  ShieldCheck,
  Zap,
  RefreshCw,
  Globe,
  Code,
  ChevronRight,
  Sparkles,
  Layers,
  Activity,
  Sliders,
  Power,
  Trash2,
  ExternalLink,
  Lock,
  Radio,
  FileText
} from 'lucide-react';

// Initial Mock Data
const INITIAL_MESSAGES = [
  {
    id: '1',
    sender: 'milo',
    text: "Hello Commander! I am **Agent Milo v4.2**, initialized and fully operational. All cognitive modules, external API toolkits, and vector memories are loaded.",
    timestamp: '10:42 AM',
    thoughts: [
      "System initialization complete.",
      "Vector database synchronized (14,230 nodes connected).",
      "Ready for autonomous workflow orchestration."
    ],
    toolsUsed: []
  },
  {
    id: '2',
    sender: 'user',
    text: "Milo, analyze our production deployment logs, check for memory leaks, and generate a optimization task workflow.",
    timestamp: '10:44 AM'
  },
  {
    id: '3',
    sender: 'milo',
    text: "I have analyzed the telemetry metrics and log streams. I detected a memory growth pattern in worker node `pod-auth-service-79x`. I have created an automated resolution task and updated our vector memory store.",
    timestamp: '10:45 AM',
    thoughts: [
      "Invoked tool `log_analyzer` with parameters: { service: 'auth-pod', window: '2h' }",
      "Detected heap allocation delta +42% over baseline.",
      "Generated workflow task #TK-892 for auto-scaling and garbage collection trigger."
    ],
    toolsUsed: [
      { name: 'Kubernetes Telemetry', duration: '120ms', status: 'success' },
      { name: 'Python Heap Diagnostic', duration: '340ms', status: 'success' }
    ]
  }
];

const INITIAL_TASKS = [
  { id: 'TK-892', title: 'Resolve Heap Memory Growth in Auth Pod', priority: 'High', status: 'In Progress', progress: 65, created: '10 mins ago', category: 'Infrastructure' },
  { id: 'TK-891', title: 'Daily AI News & ArXiv Paper Digest', priority: 'Medium', status: 'Completed', progress: 100, created: '2 hours ago', category: 'Research' },
  { id: 'TK-890', title: 'Security Vulnerability Scan (CVE Database)', priority: 'High', status: 'Completed', progress: 100, created: '5 hours ago', category: 'Security' },
  { id: 'TK-889', title: 'Synthesize Customer Sentiment Feedback', priority: 'Low', status: 'Pending', progress: 0, created: '1 day ago', category: 'Analytics' }
];

const INITIAL_MEMORIES = [
  { id: 'mem-1', type: 'Episodic', title: 'Kubernetes Auth Pod OOM Risk', memory: 'Identified recurring heap leak when JWT revocation cache exceeds 50k tokens.', relevance: 0.98, timestamp: 'Today' },
  { id: 'mem-2', type: 'Semantic', title: 'Database Primary Replica Credentials', memory: 'Stored securely in Vault path /v1/secret/db-prod with read-only scope.', relevance: 0.91, timestamp: '3 days ago' },
  { id: 'mem-3', type: 'Procedural', title: 'Automated GitHub PR Review Protocol', memory: 'Enforce TypeScript strict compliance, run unit tests, check for inline secrets before auto-merging.', relevance: 0.85, timestamp: '1 week ago' }
];

const INITIAL_TOOLS = [
  { id: 't-1', name: 'Web Search & Browser', category: 'Information Retrieval', enabled: true, usageCount: 1420, latency: '240ms', description: 'Autonomous multi-hop web browsing and real-time scraping.' },
  { id: 't-2', name: 'Python Code Sandbox', category: 'Execution', enabled: true, usageCount: 890, latency: '85ms', description: 'Isolated docker sandbox for executing analytical Python code.' },
  { id: 't-3', name: 'GitHub Integration', category: 'DevOps', enabled: true, usageCount: 320, latency: '310ms', description: 'Read/write commits, manage pull requests, and review code diffs.' },
  { id: 't-4', name: 'Vector Database (Qdrant)', category: 'Memory', enabled: true, usageCount: 5410, latency: '18ms', description: 'High-dimensional semantic vector search for past conversations and context.' },
  { id: 't-5', name: 'SQL Query Engine', category: 'Database', enabled: false, usageCount: 110, latency: '120ms', description: 'Read-only queries to production database analytics replicas.' }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('console');
  const [agentStatus, setAgentStatus] = useState('ready'); // 'ready' | 'thinking' | 'executing'
  const [messages, setMessages] = useState(INITIAL_MESSAGES);
  const [inputMsg, setInputMsg] = useState('');
  const [tasks, setTasks] = useState(INITIAL_TASKS);
  const [memories, setMemories] = useState(INITIAL_MEMORIES);
  const [tools, setTools] = useState(INITIAL_TOOLS);
  const [selectedModel, setSelectedModel] = useState('Milo-v4.2-Pro (Autonomous)');
  const [showThoughtTrace, setShowThoughtTrace] = useState(true);
  const [filterMemoryQuery, setFilterMemoryQuery] = useState('');

  // Settings State
  const [temperature, setTemperature] = useState(0.3);
  const [maxContext, setMaxContext] = useState(128);
  const [autonomousMode, setAutonomousMode] = useState(true);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, agentStatus]);

  // Handle Chat Submit
  const handleSendMessage = (e) => {
    e?.preventDefault();
    if (!inputMsg.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputMsg,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentPrompt = inputMsg;
    setInputMsg('');
    setAgentStatus('thinking');

    // Simulate Agent Thinking & Execution Lifecycle
    setTimeout(() => {
      setAgentStatus('executing');
    }, 1200);

    setTimeout(() => {
      const miloReply = {
        id: (Date.now() + 1).toString(),
        sender: 'milo',
        text: `I have processed your command: **"${currentPrompt}"**.\n\nExecuting context alignment across system modules. I have registered the instructions and queued necessary validation checks in the pipeline.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        thoughts: [
          `Parsing user prompt context: "${currentPrompt.substring(0, 30)}..."`,
          "Querying long-term semantic memory for related precedents...",
          "Selected optimal tool execution path: [Python Sandbox + Vector Query]",
          "Validation successful. Output formatted for dashboard visualizer."
        ],
        toolsUsed: [
          { name: 'Semantic Memory Search', duration: '24ms', status: 'success' },
          { name: 'Intent Classifier Module', duration: '45ms', status: 'success' }
        ]
      };
      setMessages((prev) => [...prev, miloReply]);
      setAgentStatus('ready');
    }, 3200);
  };

  const toggleTool = (id) => {
    setTools(tools.map(t => t.id === id ? { ...t, enabled: !t.enabled } : t));
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 font-sans text-slate-100">
      
      {/* LEFT NAVIGATION SIDEBAR */}
      <aside className="w-64 glass-panel border-r border-slate-800 flex flex-col justify-between z-20">
        <div>
          {/* Brand Logo & Name */}
          <div className="p-5 flex items-center gap-3 border-b border-slate-800/80">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-indigo-600 text-white shadow-lg glow-emerald">
              <Bot className="w-6 h-6" />
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
              </span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="font-bold text-base tracking-wide text-white">AGENT MILO</h1>
                <span className="text-[10px] bg-teal-500/10 text-teal-400 border border-teal-500/20 font-mono px-1.5 py-0.5 rounded">v4.2</span>
              </div>
              <p className="text-xs text-slate-400">Autonomous Intelligence</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-3 space-y-1">
            <button
              onClick={() => setActiveTab('console')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'console'
                  ? 'bg-gradient-to-r from-teal-500/20 to-indigo-500/10 border border-teal-500/30 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Terminal className="w-4 h-4" />
              Command Center
            </button>

            <button
              onClick={() => setActiveTab('workflows')}
              className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'workflows'
                  ? 'bg-gradient-to-r from-teal-500/20 to-indigo-500/10 border border-teal-500/30 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <Layers className="w-4 h-4" />
                Active Workflows
              </div>
              <span className="text-xs bg-slate-800 text-teal-400 px-2 py-0.5 rounded-full border border-slate-700">
                {tasks.filter(t => t.status === 'In Progress').length}
              </span>
            </button>

            <button
              onClick={() => setActiveTab('memory')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'memory'
                  ? 'bg-gradient-to-r from-teal-500/20 to-indigo-500/10 border border-teal-500/30 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <BrainCircuit className="w-4 h-4" />
              Vector Memory
            </button>

            <button
              onClick={() => setActiveTab('tools')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'tools'
                  ? 'bg-gradient-to-r from-teal-500/20 to-indigo-500/10 border border-teal-500/30 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Wrench className="w-4 h-4" />
              Toolbox & APIs
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'analytics'
                  ? 'bg-gradient-to-r from-teal-500/20 to-indigo-500/10 border border-teal-500/30 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              Telemetry & Usage
            </button>

            <button
              onClick={() => setActiveTab('settings')}
              className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all ${
                activeTab === 'settings'
                  ? 'bg-gradient-to-r from-teal-500/20 to-indigo-500/10 border border-teal-500/30 text-teal-300 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              <Settings className="w-4 h-4" />
              Agent Configuration
            </button>
          </nav>
        </div>

        {/* System Core Quick Stats */}
        <div className="p-4 m-3 rounded-xl bg-slate-900/80 border border-slate-800/90 text-xs space-y-2.5">
          <div className="flex justify-between items-center text-slate-400">
            <span className="flex items-center gap-1.5"><Cpu className="w-3.5 h-3.5 text-teal-400" /> Core Load</span>
            <span className="font-mono text-slate-200">12.4%</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-teal-400 h-full w-[12%] rounded-full"></div>
          </div>

          <div className="flex justify-between items-center text-slate-400 pt-1">
            <span className="flex items-center gap-1.5"><Database className="w-3.5 h-3.5 text-indigo-400" /> Token Window</span>
            <span className="font-mono text-slate-200">14.2k / 128k</span>
          </div>
          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-indigo-500 h-full w-[18%] rounded-full"></div>
          </div>
        </div>
      </aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col h-full relative overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-slate-950">
        
        {/* TOP BAR / HEADER */}
        <header className="h-16 border-b border-slate-800/80 glass-panel px-6 flex items-center justify-between z-10">
          <div className="flex items-center gap-4">
            {/* Status Indicator */}
            <div className="flex items-center gap-2.5 bg-slate-900/90 border border-slate-800 px-3 py-1.5 rounded-full text-xs font-mono">
              <span className={`w-2.5 h-2.5 rounded-full ${
                agentStatus === 'ready' ? 'bg-emerald-400 shadow-[0_0_8px_#34d399]' :
                agentStatus === 'thinking' ? 'bg-amber-400 animate-pulse' : 'bg-indigo-400 animate-ping'
              }`}></span>
              <span className="uppercase text-slate-300 tracking-wider">
                {agentStatus === 'ready' && 'SYSTEM ONLINE'}
                {agentStatus === 'thinking' && 'REASONING & PLANNING...'}
                {agentStatus === 'executing' && 'EXECUTING ACTIONS...'}
              </span>
            </div>

            {/* Model Selector Dropdown */}
            <div className="relative">
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 rounded-lg px-3 py-1.5 focus:outline-none focus:border-teal-500 cursor-pointer"
              >
                <option>Milo-v4.2-Pro (Autonomous)</option>
                <option>GPT-4o Agent Sandbox</option>
                <option>Claude 3.5 Sonnet Integration</option>
              </select>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button 
              onClick={() => setShowThoughtTrace(!showThoughtTrace)}
              className={`flex items-center gap-2 text-xs font-medium px-3 py-1.5 rounded-lg border transition-all ${
                showThoughtTrace 
                  ? 'bg-teal-500/10 border-teal-500/40 text-teal-300' 
                  : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
              }`}
            >
              <Radio className="w-3.5 h-3.5" />
              Live Telemetry Trace
            </button>

            <div className="h-4 w-[1px] bg-slate-800"></div>

            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-bold text-teal-400">
                HQ
              </div>
            </div>
          </div>
        </header>

        {/* VIEW 1: COMMAND CENTER (CHAT & LIVE TRACE) */}
        {activeTab === 'console' && (
          <div className="flex-1 flex overflow-hidden">
            {/* Main Chat Stream */}
            <div className="flex-1 flex flex-col justify-between h-full overflow-hidden">
              {/* Message List */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-xs font-semibold text-slate-400">
                        {msg.sender === 'user' ? 'Commander' : 'Agent Milo'}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">{msg.timestamp}</span>
                    </div>

                    <div
                      className={`max-w-2xl rounded-2xl p-4 text-sm leading-relaxed ${
                        msg.sender === 'user'
                          ? 'bg-indigo-600 text-white rounded-br-none shadow-md'
                          : 'glass-card text-slate-200 border border-slate-800 rounded-bl-none shadow-sm'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.text}</div>

                      {/* Tool Calls inside Milo's message */}
                      {msg.toolsUsed && msg.toolsUsed.length > 0 && (
                        <div className="mt-3 pt-3 border-t border-slate-700/50 space-y-1.5">
                          <div className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
                            <Wrench className="w-3 h-3 text-teal-400" /> Capability Invocations:
                          </div>
                          <div className="flex flex-wrap gap-2">
                            {msg.toolsUsed.map((tool, idx) => (
                              <div
                                key={idx}
                                className="flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-2.5 py-1 rounded text-xs font-mono text-teal-300"
                              >
                                <CheckCircle2 className="w-3 h-3 text-emerald-400" />
                                <span>{tool.name}</span>
                                <span className="text-[10px] text-slate-500">({tool.duration})</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}

                {/* Simulated Thinking Indicator */}
                {agentStatus !== 'ready' && (
                  <div className="flex items-center gap-3 text-slate-400 text-sm italic glass-card p-4 rounded-xl max-w-xl border border-teal-500/20">
                    <Sparkles className="w-4 h-4 text-teal-400 animate-spin" />
                    <span>
                      {agentStatus === 'thinking' ? 'Milo is deliberating and evaluating vector memory...' : 'Executing system actions and generating response...'}
                    </span>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Box */}
              <div className="p-4 glass-panel border-t border-slate-800">
                <form onSubmit={handleSendMessage} className="relative flex items-center">
                  <input
                    type="text"
                    value={inputMsg}
                    onChange={(e) => setInputMsg(e.target.value)}
                    placeholder="Command Agent Milo (e.g. 'Deploy security fix', 'Query telemetry logs')..."
                    className="w-full bg-slate-900/90 border border-slate-800 rounded-xl py-3.5 pl-4 pr-12 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500/60 focus:ring-1 focus:ring-teal-500/30 transition-all font-sans"
                  />
                  <button
                    type="submit"
                    disabled={!inputMsg.trim() || agentStatus !== 'ready'}
                    className="absolute right-2.5 bg-gradient-to-r from-teal-500 to-indigo-600 hover:from-teal-400 hover:to-indigo-500 text-white p-2 rounded-lg transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-md"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </form>
                <div className="flex justify-between items-center mt-2 px-1 text-[11px] text-slate-500">
                  <span className="flex items-center gap-1"><ShieldCheck className="w-3 h-3 text-emerald-500" /> Autonomous Guardrails Active</span>
                  <span>Press Shift + Enter for newline</span>
                </div>
              </div>
            </div>

            {/* LIVE THOUGHT TRACE PANEL (RIGHT SIDEBAR) */}
            {showThoughtTrace && (
              <div className="w-80 glass-panel border-l border-slate-800 flex flex-col h-full">
                <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                  <h3 className="text-xs font-bold font-mono tracking-wider text-slate-300 uppercase flex items-center gap-2">
                    <Activity className="w-4 h-4 text-teal-400" /> Cognitive Trace
                  </h3>
                  <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-teal-400 font-mono">LIVE STREAM</span>
                </div>

                <div className="flex-1 p-4 font-mono text-xs overflow-y-auto space-y-4 text-slate-300">
                  {messages
                    .filter(m => m.thoughts && m.thoughts.length > 0)
                    .slice(-2)
                    .map((msg, i) => (
                      <div key={i} className="space-y-2 border-b border-slate-800/80 pb-4">
                        <div className="text-[10px] text-indigo-400 font-bold">▶ TRACE BLOCK #{msg.id}</div>
                        {msg.thoughts.map((thought, idx) => (
                          <div key={idx} className="flex items-start gap-2 text-[11px] leading-relaxed text-slate-300 bg-slate-900/60 p-2 rounded border border-slate-800/50">
                            <ChevronRight className="w-3 h-3 text-teal-400 mt-0.5 shrink-0" />
                            <span>{thought}</span>
                          </div>
                        ))}
                      </div>
                    ))}

                  {agentStatus !== 'ready' && (
                    <div className="p-3 bg-teal-950/30 border border-teal-500/30 rounded-lg text-teal-300 space-y-2 animate-pulse">
                      <div className="text-[10px] font-bold text-teal-400">► ACTIVE THINKING CYCLE</div>
                      <p className="text-[11px]">Evaluating heuristics & step pipeline...</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* VIEW 2: ACTIVE WORKFLOWS */}
        {activeTab === 'workflows' && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-white">Autonomous Workflows</h2>
                <p className="text-sm text-slate-400">Monitor multi-step tasks orchestrated by Milo</p>
              </div>
              <button 
                onClick={() => {
                  const newTask = {
                    id: `TK-${Math.floor(Math.random() * 900 + 100)}`,
                    title: 'New Autonomous Pipeline Execution',
                    priority: 'Medium',
                    status: 'In Progress',
                    progress: 10,
                    created: 'Just now',
                    category: 'Automation'
                  };
                  setTasks([newTask, ...tasks]);
                }}
                className="flex items-center gap-2 bg-gradient-to-r from-teal-500 to-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold shadow-lg hover:brightness-110 transition-all"
              >
                <Plus className="w-4 h-4" /> Dispatch Workflow
              </button>
            </div>

            {/* Task Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tasks.map((task) => (
                <div key={task.id} className="glass-card p-5 rounded-xl border border-slate-800 space-y-4 hover:border-slate-700 transition-all">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-mono text-xs text-teal-400 font-semibold">{task.id}</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-slate-800 border border-slate-700 text-slate-300">{task.category}</span>
                      </div>
                      <h3 className="font-semibold text-slate-100 text-base">{task.title}</h3>
                    </div>
                    <span className={`text-xs px-2.5 py-1 rounded-full font-medium border ${
                      task.status === 'Completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                      task.status === 'In Progress' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                      'bg-slate-800 text-slate-400 border-slate-700'
                    }`}>
                      {task.status}
                    </span>
                  </div>

                  {/* Progress Bar */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs text-slate-400">
                      <span>Completion</span>
                      <span className="font-mono">{task.progress}%</span>
                    </div>
                    <div className="w-full bg-slate-900 h-2 rounded-full overflow-hidden">
                      <div 
                        className="bg-gradient-to-r from-teal-500 to-indigo-500 h-full rounded-full transition-all duration-500"
                        style={{ width: `${task.progress}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center pt-2 text-xs text-slate-400 border-t border-slate-800/60">
                    <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> Created {task.created}</span>
                    <button className="text-teal-400 hover:text-teal-300 flex items-center gap-1 font-medium">
                      Inspect Flow <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* VIEW 3: VECTOR MEMORY */}
        {activeTab === 'memory' && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold text-white">Episodic & Semantic Vector Memory</h2>
                <p className="text-sm text-slate-400">Inspect Milo's persistent high-dimensional memory embeddings</p>
              </div>
              <div className="relative w-72">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search vector embeddings..."
                  value={filterMemoryQuery}
                  onChange={(e) => setFilterMemoryQuery(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
              </div>
            </div>

            <div className="space-y-3">
              {memories
                .filter(m => m.title.toLowerCase().includes(filterMemoryQuery.toLowerCase()) || m.memory.toLowerCase().includes(filterMemoryQuery.toLowerCase()))
                .map((mem) => (
                  <div key={mem.id} className="glass-card p-4 rounded-xl border border-slate-800 flex items-start justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-mono bg-indigo-500/10 text-indigo-400 px-2 py-0.5 rounded border border-indigo-500/20">{mem.type} Memory</span>
                        <h4 className="font-semibold text-slate-100 text-sm">{mem.title}</h4>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed pt-1">{mem.memory}</p>
                    </div>

                    <div className="flex flex-col items-end gap-1 shrink-0 font-mono text-xs">
                      <span className="text-emerald-400 font-semibold">{Math.round(mem.relevance * 100)}% Match</span>
                      <span className="text-[10px] text-slate-500">{mem.timestamp}</span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        )}

        {/* VIEW 4: TOOLBOX & CAPABILITIES */}
        {activeTab === 'tools' && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Toolbox & API Capabilities</h2>
              <p className="text-sm text-slate-400">Configure external integrations Milo can invoke during execution</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tools.map((tool) => (
                <div key={tool.id} className="glass-card p-5 rounded-xl border border-slate-800 space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-teal-400">
                        <Wrench className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-white text-sm">{tool.name}</h3>
                        <span className="text-xs text-slate-400">{tool.category}</span>
                      </div>
                    </div>

                    {/* Toggle Switch */}
                    <button
                      onClick={() => toggleTool(tool.id)}
                      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                        tool.enabled ? 'bg-teal-500' : 'bg-slate-800'
                      }`}
                    >
                      <span
                        className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                          tool.enabled ? 'translate-x-6' : 'translate-x-1'
                        }`}
                      />
                    </button>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{tool.description}</p>

                  <div className="flex items-center justify-between text-xs font-mono text-slate-400 pt-2 border-t border-slate-800/60">
                    <span>Invocations: {tool.usageCount}</span>
                    <span>Latency: {tool.latency}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* VIEW 5: TELEMETRY & ANALYTICS */}
        {activeTab === 'analytics' && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            <div>
              <h2 className="text-xl font-bold text-white">Agent Telemetry & Cost</h2>
              <p className="text-sm text-slate-400">Real-time stats on token consumption, reasoning delay, and API execution</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-xs text-slate-400">Total Tokens Consumed</span>
                <div className="text-2xl font-mono font-bold text-teal-400">1,284,910</div>
                <span className="text-[10px] text-emerald-400">↑ 12% from yesterday</span>
              </div>

              <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-xs text-slate-400">Avg Decision Latency</span>
                <div className="text-2xl font-mono font-bold text-indigo-400">340 ms</div>
                <span className="text-[10px] text-teal-400">Optimal Response Time</span>
              </div>

              <div className="glass-card p-4 rounded-xl border border-slate-800 space-y-1">
                <span className="text-xs text-slate-400">Tool Call Success Rate</span>
                <div className="text-2xl font-mono font-bold text-emerald-400">99.4%</div>
                <span className="text-[10px] text-slate-500">2 errors in last 500 calls</span>
              </div>
            </div>

            {/* Performance Logs Placeholder */}
            <div className="glass-card p-5 rounded-xl border border-slate-800 space-y-3 font-mono text-xs">
              <div className="text-slate-300 font-bold flex items-center gap-2">
                <Terminal className="w-4 h-4 text-teal-400" /> SYSTEM EXECUTION TELEMETRY STREAM
              </div>
              <div className="bg-slate-950 p-4 rounded-lg space-y-1 text-slate-400 overflow-x-auto">
                <p><span className="text-teal-400">[10:45:01]</span> INFRA: Vector search response in 18ms (Qdrant Cloud)</p>
                <p><span className="text-indigo-400">[10:45:02]</span> REASON: Context compressed. Compression ratio 3.2:1</p>
                <p><span className="text-emerald-400">[10:45:03]</span> TOOL: Kubernetes API return code 200 OK</p>
                <p><span className="text-slate-500">[10:45:04]</span> CORE: Standard loop turn complete. Awaiting user input.</p>
              </div>
            </div>
          </div>
        )}

        {/* VIEW 6: AGENT CONFIGURATION */}
        {activeTab === 'settings' && (
          <div className="flex-1 p-6 overflow-y-auto space-y-6 max-w-3xl">
            <div>
              <h2 className="text-xl font-bold text-white">Agent Milo Settings</h2>
              <p className="text-sm text-slate-400">Fine-tune cognition, safety guardrails, and system persona</p>
            </div>

            <div className="glass-card p-6 rounded-xl border border-slate-800 space-y-6">
              
              {/* Temperature */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <label className="font-medium text-slate-200">Creativity / Temperature</label>
                  <span className="font-mono text-teal-400">{temperature}</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={temperature}
                  onChange={(e) => setTemperature(parseFloat(e.target.value))}
                  className="w-full accent-teal-400 bg-slate-800 rounded-lg cursor-pointer"
                />
                <p className="text-xs text-slate-400">Lower values yield deterministic execution; higher values enhance exploratory reasoning.</p>
              </div>

              {/* Context Limit */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <label className="font-medium text-slate-200">Max Context Window (k tokens)</label>
                  <span className="font-mono text-indigo-400">{maxContext}k</span>
                </div>
                <input
                  type="range"
                  min="32"
                  max="256"
                  step="32"
                  value={maxContext}
                  onChange={(e) => setMaxContext(parseInt(e.target.value))}
                  className="w-full accent-indigo-500 bg-slate-800 rounded-lg cursor-pointer"
                />
              </div>

              {/* Autonomous Mode Toggle */}
              <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                <div>
                  <h4 className="font-medium text-sm text-slate-200">Full Autonomous Execution</h4>
                  <p className="text-xs text-slate-400">Allow Milo to execute read/write tool actions without manual approval</p>
                </div>
                <button
                  onClick={() => setAutonomousMode(!autonomousMode)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    autonomousMode ? 'bg-teal-500' : 'bg-slate-800'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                      autonomousMode ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

            </div>
          </div>
        )}

      </main>
    </div>
  );
}