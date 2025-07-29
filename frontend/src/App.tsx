// Import React library to create components
import React, { useState, useEffect } from "react";

// Main App component - this is the root component that contains the entire UI
export default function App() {
  // State for simulated real-time data updates
  const [currentTime, setCurrentTime] = useState(new Date());
  const [inputVoltage, setInputVoltage] = useState(13.8);
  const [totalCurrent, setTotalCurrent] = useState(24.7);
  
  // State for managing channel statuses - each channel can be controlled
  const [channels, setChannels] = useState([
    { ch: 1, name: "FUEL PUMP", voltage: 13.2, current: 4.2, status: "ON" },
    { ch: 2, name: "IGNITION", voltage: 13.1, current: 2.1, status: "ON" },
    { ch: 3, name: "COOLING FAN", voltage: 0.0, current: 0.0, status: "OFF" },
    { ch: 4, name: "HEADLIGHTS", voltage: 12.9, current: 6.8, status: "ON" },
    { ch: 5, name: "ECU MAIN", voltage: 13.0, current: 1.5, status: "ON" },
    { ch: 6, name: "SPARE 1", voltage: 0.0, current: 0.0, status: "OFF" },
    { ch: 7, name: "SPARE 2", voltage: 0.0, current: 0.0, status: "OFF" },
    { ch: 8, name: "SPARE 3", voltage: 0.0, current: 0.0, status: "OFF" }
  ]);
  
  // State for managing system modes
  const [isTestMode, setIsTestMode] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  
  // Button click handlers - these functions will be called when buttons are pressed
  const handleResetAll = () => {
    // Emergency shutdown - cuts power to all channels immediately
    setChannels(channels.map(channel => ({
      ...channel,
      status: "OFF",
      voltage: 0.0,
      current: 0.0
    })));
    console.log("KILL SWITCH activated - all channels shut down");
  };
  
  const handleSaveConfig = () => {
    // Save current configuration (in real app, this would save to file/database)
    const config = { channels, timestamp: new Date() };
    setLastSaved(new Date());
    console.log("Configuration saved:", config);
    // In a real app, you might send this to your Rust backend
  };
  
  const handleTestMode = () => {
    // Toggle test mode - cycles through all channels for testing
    setIsTestMode(!isTestMode);
    if (!isTestMode) {
      // Turn on all channels for testing
      setChannels(channels.map(channel => ({
        ...channel,
        status: "ON",
        voltage: 13.0 + Math.random() * 0.5,
        current: 1.0 + Math.random() * 2.0
      })));
      console.log("Test mode activated - all channels ON");
    } else {
      console.log("Test mode deactivated");
    }
  };
  
  const handleLoadPreset = () => {
    // Load a predefined configuration preset
    const preset = [
      { ch: 1, name: "FUEL PUMP", voltage: 13.2, current: 4.2, status: "ON" },
      { ch: 2, name: "IGNITION", voltage: 13.1, current: 2.1, status: "ON" },
      { ch: 3, name: "COOLING FAN", voltage: 12.8, current: 8.5, status: "ON" },
      { ch: 4, name: "HEADLIGHTS", voltage: 12.9, current: 6.8, status: "ON" },
      { ch: 5, name: "ECU MAIN", voltage: 13.0, current: 1.5, status: "ON" },
      { ch: 6, name: "SPARE 1", voltage: 0.0, current: 0.0, status: "OFF" },
      { ch: 7, name: "SPARE 2", voltage: 0.0, current: 0.0, status: "OFF" },
      { ch: 8, name: "SPARE 3", voltage: 0.0, current: 0.0, status: "OFF" }
    ];
    setChannels(preset);
    console.log("Preset configuration loaded");
  };
  
  // Function to toggle individual channel on/off
  const toggleChannel = (channelNumber: number) => {
    setChannels(channels.map(channel => {
      if (channel.ch === channelNumber) {
        const newStatus = channel.status === "ON" ? "OFF" : "ON";
        return {
          ...channel,
          status: newStatus,
          voltage: newStatus === "ON" ? 13.0 + Math.random() * 0.5 : 0.0,
          current: newStatus === "ON" ? 1.0 + Math.random() * 3.0 : 0.0
        };
      }
      return channel;
    }));
    console.log(`Channel ${channelNumber} toggled`);
  };
  
  // Update time every second for realistic dashboard feel
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
      // Simulate slight voltage fluctuations
      setInputVoltage(13.8 + (Math.random() - 0.5) * 0.4);
      setTotalCurrent(24.7 + (Math.random() - 0.5) * 2.0);
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  // Calculate total power from voltage and current
  const totalPower = Math.round(inputVoltage * totalCurrent);
  
  // Return the JSX that defines what the app looks like
  return (
    // Main container - full screen with dark background (using standard Tailwind classes)
    <div className="min-h-screen bg-black text-white font-mono">
      {/* Top navigation bar - with scanning line animation */}
      <header className="bg-gray-900 border-b-2 border-blue-500 px-6 py-3 scan-line">
        <div className="flex items-center justify-between">
          {/* App branding section */}
          <div className="flex items-center space-x-4">
            {/* Logo with blue shadow effect */}
            <div className="w-10 h-10 bg-gradient-to-br from-blue-400 to-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-black font-bold text-lg">P</span>
            </div>
            <div>
              {/* App title with digital font */}
              <h1 className="text-2xl font-bold text-blue-400 font-mono">PDM CONTROLLER</h1>
              <p className="text-gray-400 text-sm">Power Distribution Module v1.0 • 8-Channel</p>
            </div>
          </div>
          
          {/* Status indicators */}
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-3">
              {/* Status indicator with green background and slow pulse animation */}
              <div className="w-4 h-4 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-green-400 font-bold tracking-wide">ONLINE</span>
            </div>
            <div className="text-right">
              {/* Digital clock display */}
              <div className="text-blue-400 font-bold font-mono text-lg">
                {currentTime.toLocaleTimeString()}
              </div>
              <div className="text-gray-400 text-xs">
                {currentTime.toLocaleDateString()}
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* Main dashboard content area */}
      <main className="p-6 grid grid-cols-12 gap-6 h-[calc(100vh-100px)]">
        {/* Left sidebar - Channel status */}
        <div className="col-span-3 space-y-4">
          <div className="bg-gray-900/80 backdrop-blur border-2 border-blue-500/30 rounded-xl p-4">
            <h2 className="text-blue-400 font-bold mb-4 text-sm uppercase tracking-wider flex items-center">
              {/* Small pulsing blue indicator */}
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
              Output Channels
            </h2>
            <div className="space-y-3">
              {/* Channel status rows - now using state that can be updated */}
              {channels.map((channel) => (
                <div 
                  key={channel.ch} 
                  onClick={() => toggleChannel(channel.ch)}
                  className={`flex items-center justify-between bg-gray-800/80 p-3 rounded-lg border-l-4 transition-all hover:bg-gray-700/80 cursor-pointer ${
                    channel.status === "ON" ? "border-green-500" : "border-gray-600"
                  }`}
                  title={`Click to ${channel.status === "ON" ? "turn OFF" : "turn ON"} ${channel.name}`}
                >
                  <div className="flex items-center space-x-3">
                    {/* Channel status indicator */}
                    <div className={`w-3 h-3 rounded-full ${
                      channel.status === "ON" ? "bg-green-500" : "bg-gray-500"
                    }`}></div>
                    <div>
                      <div className="text-white text-sm font-bold">CH{channel.ch}</div>
                      <div className="text-gray-400 text-xs">{channel.name}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    {/* Digital display values */}
                    <div className={`text-sm font-bold font-mono ${
                      channel.status === "ON" ? "text-green-400" : "text-gray-500"
                    }`}>
                      {channel.voltage.toFixed(1)}V
                    </div>
                    <div className="text-gray-500 text-xs font-mono">
                      {channel.current.toFixed(1)}A
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Center area - Main display */}
        <div className="col-span-6 space-y-4">
          {/* System overview panel */}
          <div className="bg-gray-900/80 backdrop-blur border-2 border-blue-500/30 rounded-xl p-6">
            <h2 className="text-blue-400 font-bold mb-6 text-xl uppercase tracking-wider flex items-center">
              {/* Pulsing blue indicator */}
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-3 animate-pulse"></div>
              System Overview
            </h2>
            
            {/* Key metrics grid */}
            <div className="grid grid-cols-3 gap-8 mb-8">
              <div className="text-center bg-gray-800/50 rounded-lg p-4 border border-gray-600">
                {/* Digital display with green styling */}
                <div className="text-4xl font-bold text-green-400 mb-2 font-mono">
                  {inputVoltage.toFixed(1)}V
                </div>
                <div className="text-gray-400 text-sm uppercase tracking-wide">Input Voltage</div>
                <div className="text-xs text-gray-500 mt-1">MAIN SUPPLY</div>
              </div>
              <div className="text-center bg-gray-800/50 rounded-lg p-4 border border-gray-600">
                {/* Digital display with blue styling */}
                <div className="text-4xl font-bold text-blue-400 mb-2 font-mono">
                  {totalCurrent.toFixed(1)}A
                </div>
                <div className="text-gray-400 text-sm uppercase tracking-wide">Total Current</div>
                <div className="text-xs text-gray-500 mt-1">ALL CHANNELS</div>
              </div>
              <div className="text-center bg-gray-800/50 rounded-lg p-4 border border-gray-600">
                {/* Digital display with yellow styling */}
                <div className="text-4xl font-bold text-yellow-400 mb-2 font-mono">
                  {totalPower}W
                </div>
                <div className="text-gray-400 text-sm uppercase tracking-wide">Total Power</div>
                <div className="text-xs text-gray-500 mt-1">CONSUMPTION</div>
              </div>
            </div>
            
            {/* Visual power bar */}
            <div className="mb-6">
              <div className="flex justify-between text-sm text-gray-400 mb-3">
                <span className="font-bold">POWER UTILIZATION</span>
                <span className="font-mono">{totalPower}W / 500W ({Math.round((totalPower/500)*100)}%)</span>
              </div>
              <div className="w-full bg-gray-800 rounded-full h-4 border-2 border-gray-600">
                <div 
                  className="bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 h-4 rounded-full transition-all duration-1000" 
                  style={{width: `${Math.min((totalPower/500)*100, 100)}%`}}
                ></div>
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0W</span>
                <span>250W</span>
                <span>500W</span>
              </div>
            </div>
            
            {/* Temperature monitoring */}
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-600">
                <div className="text-blue-400 text-sm font-bold mb-2">PDM TEMPERATURE</div>
                <div className="text-2xl font-bold text-green-400 font-mono">42°C</div>
                <div className="text-xs text-gray-500">Normal Operating Range</div>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4 border border-gray-600">
                <div className="text-blue-400 text-sm font-bold mb-2">AMBIENT TEMP</div>
                <div className="text-2xl font-bold text-blue-400 font-mono">23°C</div>
                <div className="text-xs text-gray-500">Environmental Sensor</div>
              </div>
            </div>
          </div>
          
          {/* Fault monitoring */}
          <div className="bg-gray-900/80 backdrop-blur border-2 border-blue-500/30 rounded-xl p-6">
            <h2 className="text-blue-400 font-bold mb-4 text-xl uppercase tracking-wider flex items-center">
              {/* Green status indicator */}
              <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
              System Status
            </h2>
            <div className="grid grid-cols-3 gap-4">
              {/* System status cards */}
              <div className="bg-green-900/40 border-2 border-green-500 rounded-lg p-4 text-center">
                <div className="text-green-400 font-bold text-lg font-mono">ALL SYSTEMS</div>
                <div className="text-green-300 text-sm">OPERATIONAL</div>
              </div>
              <div className="bg-gray-800/50 border-2 border-gray-600 rounded-lg p-4 text-center">
                <div className="text-gray-400 font-bold text-lg font-mono">0 FAULTS</div>
                <div className="text-gray-500 text-sm">DETECTED</div>
              </div>
              <div className="bg-blue-900/40 border-2 border-blue-500 rounded-lg p-4 text-center">
                <div className="text-blue-400 font-bold text-lg font-mono">MONITORING</div>
                <div className="text-blue-300 text-sm">ACTIVE</div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Right sidebar - Controls and logs */}
        <div className="col-span-3 space-y-4">
          {/* Quick controls */}
          <div className="bg-gray-900/80 backdrop-blur border-2 border-blue-500/30 rounded-xl p-4">
            <h2 className="text-blue-400 font-bold mb-4 text-sm uppercase tracking-wider flex items-center">
              {/* Pulsing blue indicator */}
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2 animate-pulse"></div>
              Quick Controls
            </h2>
            <div className="space-y-3">
              {/* Control buttons with hover effects and click handlers */}
              <button 
                onClick={handleResetAll}
                className="w-full bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white py-3 px-4 rounded-lg font-bold transition-all transform hover:scale-105"
              >
                KILL SWITCH
              </button>
              <button 
                onClick={handleSaveConfig}
                className="w-full bg-gradient-to-r from-gray-600 to-gray-700 hover:from-gray-700 hover:to-gray-800 text-white py-3 px-4 rounded-lg font-bold transition-all transform hover:scale-105"
              >
                SAVE CONFIG
                {lastSaved && <div className="text-xs text-gray-300 mt-1">Last saved: {lastSaved.toLocaleTimeString()}</div>}
              </button>
              <button 
                onClick={handleTestMode}
                className={`w-full bg-gradient-to-r transition-all transform hover:scale-105 text-white py-3 px-4 rounded-lg font-bold ${
                  isTestMode 
                    ? 'from-red-600 to-red-700 hover:from-red-700 hover:to-red-800' 
                    : 'from-yellow-600 to-yellow-700 hover:from-yellow-700 hover:to-yellow-800'
                }`}
              >
                {isTestMode ? 'EXIT TEST' : 'TEST MODE'}
              </button>
              <button 
                onClick={handleLoadPreset}
                className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white py-3 px-4 rounded-lg font-bold transition-all transform hover:scale-105"
              >
                LOAD PRESET
              </button>
            </div>
          </div>
          
          {/* Event log */}
          <div className="bg-gray-900/80 backdrop-blur border-2 border-blue-500/30 rounded-xl p-4 flex-1">
            <h2 className="text-blue-400 font-bold mb-4 text-sm uppercase tracking-wider flex items-center">
              {/* Pulsing green indicator */}
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
              Event Log
            </h2>
            {/* Event log entries with digital font */}
            <div className="space-y-2 text-xs font-mono max-h-64 overflow-y-auto">
              <div className="text-green-400 border-l-2 border-green-500 pl-2">
                {currentTime.toLocaleTimeString()} - System initialized
              </div>
              <div className="text-blue-400 border-l-2 border-blue-500 pl-2">
                {new Date(currentTime.getTime() - 1000).toLocaleTimeString()} - All channels online
              </div>
              <div className="text-yellow-400 border-l-2 border-yellow-500 pl-2">
                {new Date(currentTime.getTime() - 5000).toLocaleTimeString()} - Configuration loaded
              </div>
              <div className="text-gray-400 border-l-2 border-gray-500 pl-2">
                {new Date(currentTime.getTime() - 8000).toLocaleTimeString()} - CAN bus active
              </div>
              <div className="text-green-400 border-l-2 border-green-500 pl-2">
                {new Date(currentTime.getTime() - 12000).toLocaleTimeString()} - USB connected
              </div>
              <div className="text-blue-400 border-l-2 border-blue-500 pl-2">
                {new Date(currentTime.getTime() - 15000).toLocaleTimeString()} - Ready for operation
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
