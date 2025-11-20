<script>
  import { onMount } from 'svelte';
  
  let currentPage = $state('home');
  let measurements = $state([]);
  let stats = $state({ avgDownload: 0, avgUpload: 0, avgPing: 0, totalTests: 0 });
  let isLoading = $state(true);
  let error = $state(null);
  let lastUpdate = $state('');
  let graphs = $state([]);
  let graphsLoading = $state(false);

  const API_BASE = 'http://localhost:5001';

  async function loadMeasurements() {
    try {
      console.log('🔄 Lade Messungen von:', `${API_BASE}/measurements`);
      const response = await fetch(`${API_BASE}/measurements?limit=50`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('✅ Daten empfangen:', data);
      
      measurements = data.measurements || [];
      lastUpdate = new Date().toLocaleTimeString('de-DE');
      
      if (measurements.length > 0) {
        calculateStats();
      }
      
      error = null;
      isLoading = false;
    } catch (e) {
      console.error('❌ Fehler beim Laden:', e);
      error = `Backend-Verbindung fehlgeschlagen: ${e.message}`;
      isLoading = false;
    }
  }

  function calculateStats() {
    if (measurements.length === 0) return;
    
    const total = measurements.length;
    const sumDownload = measurements.reduce((sum, m) => sum + parseFloat(m.download_Mbps || 0), 0);
    const sumUpload = measurements.reduce((sum, m) => sum + parseFloat(m.upload_Mbps || 0), 0);
    const sumPing = measurements.reduce((sum, m) => sum + parseFloat(m.ping_ms || 0), 0);
    
    stats = {
      avgDownload: (sumDownload / total).toFixed(2),
      avgUpload: (sumUpload / total).toFixed(2),
      avgPing: (sumPing / total).toFixed(2),
      totalTests: total
    };
  }

  async function generateGraphs() {
    try {
      graphsLoading = true;
      const response = await fetch(`${API_BASE}/graphs/generate`, { method: 'POST' });
      if (response.ok) {
        alert('✅ Grafiken wurden aktualisiert!');
        await loadGraphsList();
      }
    } catch (error) {
      console.error('Fehler beim Generieren der Grafiken:', error);
      alert('❌ Fehler beim Generieren der Grafiken');
    } finally {
      graphsLoading = false;
    }
  }

  async function loadGraphsList() {
    try {
      const response = await fetch(`${API_BASE}/graphs/list`);
      const data = await response.json();
      graphs = data.graphs || [];
      console.log('📊 Grafiken geladen:', graphs);
    } catch (error) {
      console.error('Fehler beim Laden der Grafiken:', error);
    }
  }

  function navigate(page) {
    currentPage = page;
    if (page === 'graphs') {
      loadGraphsList();
    }
  }

  function exportCSV() {
    window.open(`${API_BASE}/export/csv`, '_blank');
  }

  const latestMeasurement = $derived(measurements.length > 0 ? measurements[0] : null);

  onMount(() => {
    console.log('🚀 App gestartet - API Base:', API_BASE);
    loadMeasurements();
    loadGraphsList();
    
    const interval = setInterval(() => {
      console.log('🔄 Auto-Refresh...');
      loadMeasurements();
    }, 10000);
    
    return () => clearInterval(interval);
  });
</script>

<main>
  {#if isLoading}
    <div class="container">
      <div class="loading">
        <h1>⏳ Lade Daten...</h1>
        <p>Verbinde mit {API_BASE}</p>
      </div>
    </div>
  {:else if error}
    <div class="container">
      <div class="error-box">
        <h1>❌ Verbindungsfehler</h1>
        <p>{error}</p>
        <p class="hint">Stelle sicher, dass das Backend läuft: <code>python py/Main.py</code></p>
        <button onclick={loadMeasurements} class="retry-btn">🔄 Erneut versuchen</button>
      </div>
    </div>
  {:else if currentPage === 'home'}
    <div class="container">
      <div class="header">
        <h1>🚀 DaLohyn SpeedWatch 🚀</h1>
        <p class="subtitle">Internet-Geschwindigkeitsüberwachung</p>
        <p class="update-time">Letzte Aktualisierung: {lastUpdate}</p>
      </div>
      
      {#if latestMeasurement}
        <div class="speed-display">
          <div class="measurement-grid">
            <div class="measurement-item">
              <div class="measurement-label">📥 Download</div>
              <div class="measurement-value">{parseFloat(latestMeasurement.download_Mbps).toFixed(2)}</div>
              <div class="measurement-unit">Mbps</div>
            </div>
            <div class="measurement-item">
              <div class="measurement-label">📤 Upload</div>
              <div class="measurement-value">{parseFloat(latestMeasurement.upload_Mbps).toFixed(2)}</div>
              <div class="measurement-unit">Mbps</div>
            </div>
            <div class="measurement-item">
              <div class="measurement-label">🏓 Ping</div>
              <div class="measurement-value">{parseFloat(latestMeasurement.ping_ms).toFixed(1)}</div>
              <div class="measurement-unit">ms</div>
            </div>
          </div>
          
          <div class="server-info">
            <div>🖥️ Server: {latestMeasurement.server}</div>
            <div>📍 Standort: {latestMeasurement.server_location}, {latestMeasurement.server_country}</div>
            <div>🌐 IP: {latestMeasurement.ip}</div>
            <div>📉 Packet Loss: {latestMeasurement.packet_loss}%</div>
            <div>⏰ Letzte Messung: {latestMeasurement.time}</div>
          </div>
        </div>
      {:else}
        <div class="no-data">
          <p>📊 Keine Messungen vorhanden</p>
          <p class="small">Das Backend läuft und hat {measurements.length} Messungen</p>
          <p class="small">Starte einen Test mit: <code>python py/Main.py</code></p>
          <button onclick={loadMeasurements} class="retry-btn">🔄 Neu laden</button>
        </div>
      {/if}

      <div class="recent-measurements">
        <h2>📊 Letzte Messungen ({measurements.length})</h2>
        {#if measurements.length > 0}
          <div class="measurements-list">
            {#each measurements.slice(0, 10) as measurement}
              <div class="measurement-card">
                <div class="measurement-time">{measurement.time}</div>
                <div class="measurement-details">
                  <span>📥 {parseFloat(measurement.download_Mbps).toFixed(2)} Mbps</span>
                  <span>📤 {parseFloat(measurement.upload_Mbps).toFixed(2)} Mbps</span>
                  <span>🏓 {parseFloat(measurement.ping_ms).toFixed(1)} ms</span>
                </div>
              </div>
            {/each}
          </div>
        {:else}
          <p class="no-data-text">Keine Messungen vorhanden</p>
        {/if}
      </div>

      <div class="nav">
        <button onclick={() => navigate('statistics')}>📊 Alle Messungen</button>
        <button onclick={() => navigate('graphs')}>📈 Grafiken</button>
        <button onclick={exportCSV}>💾 CSV Download</button>
      </div>
    </div>

  {:else if currentPage === 'statistics'}
    <div class="container">
      <h1>📊 Statistiken</h1>
      
      <div class="stats-grid">
        <div class="stat-card">
          <h3>⌀ Download</h3>
          <div class="stat-value">{stats.avgDownload} Mbps</div>
        </div>
        <div class="stat-card">
          <h3>⌀ Upload</h3>
          <div class="stat-value">{stats.avgUpload} Mbps</div>
        </div>
        <div class="stat-card">
          <h3>⌀ Ping</h3>
          <div class="stat-value">{stats.avgPing} ms</div>
        </div>
        <div class="stat-card">
          <h3>Gesamte Tests</h3>
          <div class="stat-value">{stats.totalTests}</div>
        </div>
      </div>

      <div class="all-measurements">
        <h2>📋 Alle Messungen</h2>
        <div class="measurements-list">
          {#each measurements as measurement}
            <div class="measurement-card">
              <div class="measurement-time">{measurement.time}</div>
              <div class="measurement-details">
                <span>📥 {parseFloat(measurement.download_Mbps).toFixed(2)} Mbps</span>
                <span>📤 {parseFloat(measurement.upload_Mbps).toFixed(2)} Mbps</span>
                <span>🏓 {parseFloat(measurement.ping_ms).toFixed(1)} ms</span>
                <span>📍 {measurement.server_location}, {measurement.server_country}</span>
              </div>
            </div>
          {/each}
        </div>
      </div>

      <button class="back-btn" onclick={() => navigate('home')}>← Zurück</button>
    </div>
  {:else if currentPage === 'graphs'}
    <div class="container">
      <h1>📈 Grafiken & Visualisierungen</h1>
      
      <div class="graph-controls">
        <button onclick={generateGraphs} class="generate-btn" disabled={graphsLoading}>
          {graphsLoading ? '⏳ Generiere...' : '🔄 Grafiken aktualisieren'}
        </button>
        <button onclick={() => navigate('home')} class="back-btn-inline">
          ← Zurück
        </button>
      </div>

      {#if graphs.length > 0}
        <div class="graphs-grid">
          {#each graphs as graph}
            <div class="graph-card">
              <h3>{graph.name}</h3>
              <div class="graph-wrapper">
                <img 
                  src="{API_BASE}{graph.url}?t={Date.now()}" 
                  alt={graph.name}
                  class="graph-image"
                />
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="no-graphs">
          <p>📊 Noch keine Grafiken vorhanden</p>
          <p class="small">Klicke auf "Grafiken aktualisieren" um Visualisierungen zu erstellen</p>
        </div>
      {/if}
    </div>
  {/if}
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
  }

  main {
    padding: 2rem;
    min-height: 100vh;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  .loading,
  .error-box {
    background: rgba(255, 255, 255, 0.95);
    padding: 4rem;
    border-radius: 20px;
    text-align: center;
    margin-top: 5rem;
  }

  .error-box h1 {
    color: #f44336;
  }

  .error-box p {
    color: #666;
    font-size: 1.2rem;
    margin: 1rem 0;
  }

  .retry-btn {
    padding: 1rem 2rem;
    background: #667eea;
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 1.1rem;
    cursor: pointer;
    margin-top: 1rem;
  }

  .header {
    text-align: center;
    margin-bottom: 3rem;
  }

  h1 {
    color: #fff;
    font-size: 3rem;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
  }

  h2 {
    color: #333;
    margin-bottom: 1.5rem;
  }

  h3 {
    font-size: 1rem;
    color: #666;
    margin-bottom: 1rem;
  }

  .subtitle {
    color: rgba(255, 255, 255, 0.9);
    font-size: 1.2rem;
  }

  .speed-display {
    background: rgba(255, 255, 255, 0.95);
    padding: 3rem;
    border-radius: 20px;
    margin: 2rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  }

  .measurement-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2rem;
    margin-bottom: 2rem;
  }

  .measurement-item {
    text-align: center;
  }

  .measurement-label {
    font-size: 1rem;
    color: #666;
    margin-bottom: 0.5rem;
  }

  .measurement-value {
    font-size: 4rem;
    font-weight: bold;
    color: #667eea;
  }

  .measurement-unit {
    font-size: 1.3rem;
    color: #999;
  }

  .server-info {
    margin-top: 2rem;
    padding-top: 2rem;
    border-top: 2px solid #f0f0f0;
    text-align: left;
    color: #555;
    line-height: 2;
  }

  .no-data {
    background: rgba(255, 255, 255, 0.95);
    padding: 4rem 2rem;
    border-radius: 20px;
    text-align: center;
  }

  .no-data p {
    font-size: 1.3rem;
    color: #666;
    margin: 0.5rem 0;
  }

  .small {
    font-size: 1rem;
    color: #999;
  }

  code {
    background: #f0f0f0;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-family: monospace;
  }

  .recent-measurements {
    margin-top: 4rem;
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  }

  .measurements-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .measurement-card {
    background: #f8f9fa;
    padding: 1.2rem;
    border-radius: 12px;
    border-left: 4px solid #667eea;
  }

  .measurement-time {
    font-weight: 600;
    color: #333;
    margin-bottom: 0.8rem;
  }

  .measurement-details {
    display: flex;
    gap: 2rem;
    color: #666;
    flex-wrap: wrap;
  }

  .no-data-text {
    color: #999;
    font-style: italic;
    padding: 2rem;
  }

  .nav {
    margin-top: 3rem;
    display: flex;
    gap: 1rem;
    justify-content: center;
  }

  .nav button {
    padding: 1rem 2rem;
    background: rgba(255, 255, 255, 0.95);
    color: #667eea;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  }

  .nav button:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
  }

  .stat-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }

  .stat-value {
    font-size: 3rem;
    font-weight: bold;
    color: #667eea;
  }

  .all-measurements {
    margin-top: 3rem;
    background: rgba(255, 255, 255, 0.95);
    padding: 2rem;
    border-radius: 20px;
    max-height: 600px;
    overflow-y: auto;
  }

  .back-btn {
    margin-top: 3rem;
    padding: 1rem 2rem;
    background: rgba(255, 255, 255, 0.95);
    color: #667eea;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 1.1rem;
    font-weight: 600;
  }

  .update-time {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.9rem;
    margin-top: 0.5rem;
  }

  .graph-controls {
    margin: 2rem 0;
    display: flex;
    gap: 1rem;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
  }

  .generate-btn {
    padding: 1rem 2rem;
    background: #4CAF50;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1.1rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    transition: all 0.3s ease;
  }

  .generate-btn:hover:not(:disabled) {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
  }

  .generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .back-btn-inline {
    padding: 1rem 2rem;
    background: rgba(255, 255, 255, 0.95);
    color: #667eea;
    border: none;
    border-radius: 12px;
    cursor: pointer;
    font-size: 1.1rem;
    font-weight: 600;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }

  .back-btn-inline:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
  }

  .graphs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
    gap: 2rem;
    margin: 3rem 0;
  }

  .graph-card {
    background: rgba(255, 255, 255, 0.95);
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }

  .graph-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  }

  .graph-card h3 {
    color: #333;
    margin-bottom: 1rem;
    text-align: center;
    font-size: 1.2rem;
  }

  .graph-wrapper {
    width: 100%;
    background: white;
    border-radius: 8px;
    padding: 0.5rem;
  }

  .graph-image {
    width: 100%;
    height: auto;
    border-radius: 8px;
    display: block;
  }

  .no-graphs {
    background: rgba(255, 255, 255, 0.95);
    padding: 4rem 2rem;
    border-radius: 20px;
    text-align: center;
    margin: 3rem 0;
  }

  .no-graphs p {
    font-size: 1.3rem;
    color: #666;
    margin: 0.5rem 0;
  }

  .no-graphs .small {
    font-size: 1rem;
    color: #999;
  }

  @media (max-width: 768px) {
    .measurement-grid {
      grid-template-columns: 1fr;
    }

    .graphs-grid {
      grid-template-columns: 1fr;
    }
  }
</style>
