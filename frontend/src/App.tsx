import React, { useEffect, useState } from "react";
import { pdmApi, TestScenario, Channel } from "./api/client";

export default function App() {
  // Theme
  const [theme, setTheme] = useState<"fiu" | "fiu-dark">(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "fiu" || saved === "fiu-dark") return saved as any;
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    return prefersDark ? "fiu-dark" : "fiu";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  // Realtime + system state
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [systemVoltage, setSystemVoltage] = useState(0);
  const [totalCurrent, setTotalCurrent] = useState(0);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [systemStatus, setSystemStatus] = useState("Normal");

  // Test cases
  const [isTestMode, setIsTestMode] = useState(false);
  const [testScenario, setTestScenario] = useState<TestScenario>({
    name: "",
    description: "",
    elapsed: 0,
    status: "idle",
    current_event: "",
  });

  // Clock
  useEffect(() => {
    const t = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // Poll backend
  useEffect(() => {
    let mounted = true;
    const tick = async () => {
      try {
        const status = await pdmApi.getStatus();
        if (!mounted) return;
        setIsConnected(true);
        setSystemVoltage(status.system_voltage || 0);
        setTotalCurrent(status.total_current || 0);
        setChannels(status.channels || []);
        setLastUpdate(new Date(status.timestamp || Date.now()));
        setSystemStatus("Normal");
      } catch (e) {
        if (!mounted) return;
        setIsConnected(false);
        setSystemStatus("Offline");
      }
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  // Poll test scenario when test mode is on
  useEffect(() => {
    if (!isTestMode) return;
    let mounted = true;
    const tick = async () => {
      try {
        const scen = await pdmApi.getTestScenario();
        if (mounted) setTestScenario(scen);
      } catch {}
    };
    tick();
    const id = setInterval(tick, 500);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, [isTestMode]);

  // Handlers
  const toggleChannel = async (channelNumber: number) => {
    const channelIndex = channelNumber - 1;
    
    // Capture current state immediately to avoid race with polling
    setChannels((prev) => {
      const target = !(prev[channelIndex]?.status?.on ?? false);
      const next = [...prev];
      
      if (next[channelIndex]) {
        next[channelIndex] = {
          ...next[channelIndex],
          status: { ...next[channelIndex].status, on: target },
        } as Channel;
        
        // API call in background - use channelIndex (0-7) not channelNumber (1-8)
        pdmApi.controlChannel(channelIndex, target)
          .then((res) => {
            console.log(`Channel ${channelNumber} -> ${target ? "ON" : "OFF"} | in_use=${res?.in_use}`);
          })
          .catch((e) => {
            console.error("Failed to toggle channel", e);
            // Revert on error
            setChannels((prev2) => {
              const next2 = [...prev2];
              if (next2[channelIndex]) {
                next2[channelIndex] = {
                  ...next2[channelIndex],
                  status: { ...next2[channelIndex].status, on: !target },
                } as Channel;
              }
              return next2;
            });
          });
      }
      
      return next;
    });
  };

  const handleResetAll = async () => {
    // Optional: iterate channels and turn off
    for (const ch of channels) {
      if (ch.status?.on) {
        try { await pdmApi.controlChannel(ch.id + 1, false); } catch {}
      }
    }
  };

  const handleSaveConfig = () => {
    setLastSaved(new Date());
  };

  const handleTestMode = () => {
    setIsTestMode((v) => !v);
    if (isTestMode) {
      setTestScenario({ name: "", description: "", elapsed: 0, status: "idle", current_event: "" });
    }
  };

  const triggerScenario = async (id: number) => {
    try {
      await pdmApi.triggerScenario(id);
      // Poll immediately to pick up the active scenario
      const scen = await pdmApi.getTestScenario();
      setTestScenario(scen);
    } catch (e) {
      console.error("Failed to trigger scenario", e);
    }
  };

  // Derived
  const totalPower = Math.round(systemVoltage * totalCurrent);
  const avgTemperature = channels.length > 0
    ? channels.reduce((sum, ch) => sum + (ch.temperature || 0), 0) / channels.length
    : 0;

  return (
    <div className="min-h-screen bg-base-100 text-base-content font-sans">
      {/* Top navigation bar */}
      <header className="navbar bg-base-200 border-b border-base-300 px-6 py-3">
        <div className="flex items-center justify-between w-full">
          {/* Branding */}
          <div className="flex items-center space-x-4">
            <div className="w-10 h-10 bg-gradient-to-br from-accent to-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-extrabold text-lg">13</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-primary">PDM CONTROLLER</h1>
              <p className="text-base-content/70 text-sm">Power Distribution Module v1.0 • 8-Channel</p>
            </div>
          </div>

          {/* Centered theme toggle */}
          <div className="flex-1 flex items-center justify-center">
            <div className="join join-horizontal">
              <button className={`btn btn-ghost btn-sm join-item ${theme === 'fiu' ? 'btn-active' : ''}`} onClick={() => setTheme('fiu')} title="FIU Light">Light</button>
              <button className={`btn btn-ghost btn-sm join-item ${theme === 'fiu-dark' ? 'btn-active' : ''}`} onClick={() => setTheme('fiu-dark')} title="FIU Dark">Dark</button>
            </div>
          </div>

          {/* Status (top-right) */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center space-x-3">
              <div className={`w-4 h-4 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <span className={`font-bold tracking-wide ${isConnected ? 'text-success' : 'text-error'}`}>
                {isConnected ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-base-content font-bold font-mono text-lg">{currentTime.toLocaleTimeString()}</div>
              <div className="text-base-content/70 text-xs">{currentTime.toLocaleDateString()}</div>
              {lastUpdate && (
                <div className="text-base-content/60 text-xs mt-1">Last Update: {lastUpdate.toLocaleTimeString()}</div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main area */}
      <main className="p-6 grid grid-cols-12 gap-6 h-[calc(100vh-100px)]">
        {/* Left sidebar - channels */}
        <div className="col-span-3 space-y-4">
          <div className="bg-base-200 border border-base-300 rounded-xl p-4 shadow">
            <h2 className="text-base-content font-bold mb-4 text-sm uppercase tracking-wider flex items-center">
              <div className="w-2 h-2 bg-secondary rounded-full mr-2 animate-pulse"></div>
              Output Channels
            </h2>
            <div className="space-y-2">
              {channels.map((channel) => {
                const isOn = channel.status?.on || false;
                const hasFault = Boolean(channel.status?.fault || channel.status?.over_current || channel.status?.over_temp);
                return (
                  <div
                    key={channel.id}
                    onClick={() => toggleChannel(channel.id + 1)}
                    className={`flex items-center justify-between bg-base-300 p-3 rounded-lg border-l-4 transition-all hover:bg-base-300/80 cursor-pointer ${hasFault ? 'border-error' : isOn ? 'border-success' : 'border-base-300'}`}
                    title={`Click to ${isOn ? 'turn OFF' : 'turn ON'} ${channel.name}`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className={`w-2.5 h-2.5 rounded-full ${isOn ? (hasFault ? 'bg-error' : 'bg-success') : 'bg-base-300'}`}></div>
                      <div className="text-center">
                        <div className="text-base-content text-xs font-bold uppercase">{channel.name}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xl font-bold font-mono ${hasFault ? 'text-error' : isOn ? 'text-success' : 'text-base-content/50'}`}>{channel.current.toFixed(1)}A</div>
                      <div className="text-base-content/60 text-[10px] font-mono">{channel.voltage.toFixed(1)}V</div>
                      <div className="mt-0.5 space-x-1">
                        {isOn ? (<span className="badge badge-success badge-xs text-[9px] py-0">ON</span>) : (<span className="badge badge-ghost badge-xs text-[9px] py-0">OFF</span>)}
                        {hasFault && <span className="badge badge-error badge-xs text-[9px] py-0">FAULT</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Center - system overview */}
        <div className="col-span-6 space-y-4">
          {/* System overview panel */}
          <div className="bg-base-200 border border-base-300 rounded-xl p-6 shadow">
            <h2 className="text-base-content font-bold mb-6 text-xl uppercase tracking-wider flex items-center">
              {/* Pulsing blue indicator */}
              <div className="w-3 h-3 bg-secondary rounded-full mr-3 animate-pulse"></div>
              System Overview
            </h2>
            
            {/* Key metrics grid */}
            <div className="grid grid-cols-3 gap-8 mb-8">
              <div className="text-center bg-base-300 rounded-lg p-4 border border-base-300">
                {/* Digital display with green styling */}
                <div className="text-4xl font-bold text-success mb-2 font-mono">
                  {systemVoltage.toFixed(1)}V
                </div>
                <div className="text-base-content/70 text-sm uppercase tracking-wide">System Voltage</div>
                <div className="text-xs text-base-content/50 mt-1">MAIN SUPPLY</div>
              </div>
              <div className="text-center bg-base-300 rounded-lg p-4 border border-base-300">
                {/* Digital display with neutral styling */}
                <div className="text-4xl font-bold text-base-content/70 mb-2 font-mono">
                  {totalCurrent.toFixed(1)}A
                </div>
                <div className="text-base-content/70 text-sm uppercase tracking-wide">Total Current</div>
                <div className="text-xs text-base-content/50 mt-1">ALL CHANNELS</div>
              </div>
              <div className="text-center bg-base-300 rounded-lg p-4 border border-base-300">
                {/* Digital display with yellow styling */}
                <div className="text-4xl font-bold text-warning mb-2 font-mono">
                  {totalPower}W
                </div>
                <div className="text-base-content/70 text-sm uppercase tracking-wide">Total Power</div>
                <div className="text-xs text-base-content/50 mt-1">CONSUMPTION</div>
              </div>
            </div>
            
            {/* Visual power bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-400 mb-3">
                <span className="font-bold">POWER UTILIZATION</span>
                <span className="font-mono">{totalPower}W / 500W ({Math.round((totalPower/500)*100)}%)</span>
              </div>
              <div className="w-full bg-base-300 rounded-full h-4 border border-base-300">
                <div 
                  className="bg-gradient-to-r from-success via-warning to-error h-4 rounded-full transition-all duration-1000" 
                  style={{width: `${Math.min((totalPower/500)*100, 100)}%`}}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-base-content/50 mt-1">
                <span>0W</span>
                <span>250W</span>
                <span>500W</span>
              </div>
            </div>
            
            {/* Temperature monitoring */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-base-300 rounded-lg p-4 border border-base-300">
                <div className="text-base-content font-bold text-sm mb-2">AVG TEMPERATURE</div>
                <div className={`text-2xl font-bold font-mono ${avgTemperature > 50 ? 'text-red-400' : avgTemperature > 40 ? 'text-yellow-400' : 'text-green-400'}`}>
                  {avgTemperature.toFixed(1)}°C
                </div>
                <div className="text-xs text-base-content/50">
                  {avgTemperature > 50 ? 'WARNING - High Temp' : 'Normal Operating Range'}
                </div>
              </div>
              <div className="bg-base-300 rounded-lg p-4 border border-base-300">
                <div className="text-base-content font-bold text-sm mb-2">SYSTEM STATUS</div>
                <div className={`text-2xl font-bold font-mono ${
                  systemStatus === 'Fault' ? 'text-error' :
                  systemStatus === 'Warning' ? 'text-warning' :
                  systemStatus === 'Emergency' ? 'text-error' :
                  'text-success'
                }`}>
                  {systemStatus.toUpperCase()}
                </div>
                <div className="text-xs text-base-content/50">Backend Connection</div>
              </div>
            </div>
          </div>
          
          {/* Fault monitoring */}
          <div className="bg-base-200 border border-base-300 rounded-xl p-6 shadow">
            <h2 className="text-base-content font-bold mb-4 text-xl uppercase tracking-wider flex items-center">
              {/* Green status indicator */}
              <div className="w-3 h-3 bg-success rounded-full mr-3"></div>
              System Status
            </h2>
            <div className="grid grid-cols-3 gap-4">
              {/* System status cards */}
              <div className="bg-success/20 border border-success rounded-lg p-4 text-center">
                <div className="text-success font-bold text-lg font-mono">ALL SYSTEMS</div>
                <div className="text-success/80 text-sm">OPERATIONAL</div>
              </div>
              <div className="bg-base-300 border border-base-300 rounded-lg p-4 text-center">
                <div className="text-base-content/70 font-bold text-lg font-mono">0 FAULTS</div>
                <div className="text-base-content/50 text-sm">DETECTED</div>
              </div>
              <div className="bg-warning/20 border border-warning rounded-lg p-4 text-center">
                <div className="text-warning font-bold text-lg font-mono">MONITORING</div>
                <div className="text-warning/80 text-sm">ACTIVE</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right sidebar - Controls and logs */}
        <div className="col-span-3 space-y-4">
          {/* Quick controls */}
          <div className="bg-base-200 border border-base-300 rounded-xl p-4 shadow">
            <h2 className="text-base-content font-bold mb-4 text-sm uppercase tracking-wider flex items-center">
              {/* Pulsing blue indicator */}
              <div className="w-2 h-2 bg-secondary rounded-full mr-2 animate-pulse"></div>
              Quick Controls
            </h2>
            <div className="space-y-3">
              {/* Control buttons with hover effects and click handlers */}
              <button
                onClick={handleResetAll}
                className="btn btn-error btn-block"
              >
                KILL SWITCH
              </button>
              <button
                onClick={handleSaveConfig}
                className="btn btn-success btn-block"
              >
                SAVE CONFIG
              </button>
              {lastSaved && (
                <div className="text-xs text-base-content/60 text-center">Last saved: {lastSaved.toLocaleTimeString()}</div>
              )}
              <button
                onClick={handleTestMode}
                className={`btn btn-block ${isTestMode ? 'btn-error' : 'btn-warning'}`}
              >
                {isTestMode ? 'CLOSE TEST CASES' : 'TEST CASES'}
              </button>
            </div>
          </div>
          
          {/* Event log */}
          <div className="bg-base-200 border border-base-300 rounded-xl p-4 flex-1">
            <h2 className="text-base-content font-bold mb-4 text-sm uppercase tracking-wider flex items-center">
              {/* Pulsing green indicator */}
              <div className="w-2 h-2 bg-success rounded-full mr-2 animate-pulse"></div>
              Event Log
            </h2>
            {/* Event log entries with digital font */}
            <div className="space-y-2 text-xs font-mono max-h-64 overflow-y-auto">
              <div className="text-success border-l-2 border-success pl-2">
                {currentTime.toLocaleTimeString()} - System initialized
              </div>
              <div className="text-info border-l-2 border-info pl-2">
                {new Date(currentTime.getTime() - 1000).toLocaleTimeString()} - All channels online
              </div>
              <div className="text-warning border-l-2 border-warning pl-2">
                {new Date(currentTime.getTime() - 5000).toLocaleTimeString()} - Configuration loaded
              </div>
              <div className="text-base-content/60 border-l-2 border-base-300 pl-2">
                {new Date(currentTime.getTime() - 8000).toLocaleTimeString()} - CAN bus active
              </div>
              <div className="text-success border-l-2 border-success pl-2">
                {new Date(currentTime.getTime() - 12000).toLocaleTimeString()} - USB connected
              </div>
              <div className="text-info border-l-2 border-info pl-2">
                {new Date(currentTime.getTime() - 15000).toLocaleTimeString()} - Ready for operation
              </div>
            </div>
          </div>
        </div>
      </main>
      
      {/* Test Cases Panel - Bottom Right (shown when Test Cases toggled) */}
      {isTestMode && (
      <div className="fixed bottom-6 right-6 w-96 bg-base-200 border border-base-300 rounded-lg shadow-xl p-5 text-base-content">
        <div className="border-b border-base-300 pb-3 mb-4">
          <h3 className="text-xl font-bold text-primary">Test Cases</h3>
          <p className="text-xs text-base-content/70 mt-1">Simulate real-world race conditions</p>
        </div>
        
        {testScenario.status === 'idle' ? (
          // Idle state - show scenario buttons
          <div className="space-y-3">
            <p className="text-sm text-base-content/80 font-medium mb-3">Select a scenario:</p>
            <button
              onClick={() => triggerScenario(1)}
              className="btn btn-secondary btn-block"
            >
              Cooling Fan Failure
            </button>
            <button
              onClick={() => triggerScenario(2)}
              className="btn btn-secondary btn-block"
            >
              Engine Start Sequence
            </button>
            <div className="mt-4 pt-3 border-t border-base-300">
              <div className="flex items-center text-sm text-success">
                <div className="w-2 h-2 bg-success rounded-full mr-2"></div>
                <span className="font-medium">Status: Ready</span>
              </div>
            </div>
          </div>
        ) : testScenario.status === 'active' ? (
          // Active state - show scenario running
          <div className="space-y-3">
            <div className="bg-base-300 border-l-4 border-secondary p-3 rounded">
              <h4 className="font-bold text-secondary text-lg">{testScenario.name}</h4>
              <p className="text-sm text-base-content/70 mt-1">{testScenario.description}</p>
            </div>
            
            <div className="bg-base-300 rounded-lg p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-base-content/80">Time Elapsed:</span>
                <span className="text-lg font-bold text-secondary">{testScenario.elapsed.toFixed(1)}s</span>
              </div>
            </div>
            
            <div className="bg-base-300 rounded-lg p-3 max-h-48 overflow-y-auto">
              <h5 className="text-xs font-bold text-base-content/80 mb-2 uppercase">Event Log:</h5>
              <div className="space-y-1 text-xs font-mono">
                <div className="text-secondary border-l-2 border-secondary pl-2 py-1">
                  {testScenario.current_event}
                </div>
              </div>
            </div>
            
            <div className="flex items-center text-sm text-secondary bg-base-300 p-2 rounded">
              <div className="w-2 h-2 bg-secondary rounded-full mr-2 animate-pulse"></div>
              <span className="font-medium">Status: Active</span>
            </div>
          </div>
        ) : (
          // Complete state
          <div className="space-y-3">
            <div className="bg-base-300 border-l-4 border-success p-3 rounded">
              <h4 className="font-bold text-success text-lg">✅ Scenario Complete</h4>
              <p className="text-sm text-base-content/70 mt-1">Returning to normal mode...</p>
            </div>
          </div>
        )}
      </div>
      )}
    </div>
  );
}
