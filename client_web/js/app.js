// client_web/js/app.js
// Composant principal de l'application
// import React, { useState, useEffect, useCallback, Fragment } from 'react'; // Supprimé

const App = () => {
    const [activeView, setActiveView] = React.useState('dashboard'); // 'dashboard', 'agents', 'graph'
    const [agents, setAgents] = React.useState([]);
    const [loadingError, setLoadingError] = React.useState(null);

    const fetchAgents = React.useCallback(async () => {
        try {
            setLoadingError(null);
            const response = await fetch(`${C2_SERVER_URL}/agents`);
            if (!response.ok) {
                throw new Error(`Erreur HTTP: ${response.status} ${response.statusText}`);
            }
            const data = await response.json();
            setAgents(data);
        } catch (error) {
            console.error("Erreur de chargement des agents:", error);
            setLoadingError(`Impossible de charger les agents: ${error.message}. Vérifiez que le serveur C2 est lancé sur ${C2_SERVER_URL}.`);
            setAgents([]); // Vider les agents en cas d'erreur
        }
    }, [C2_SERVER_URL]); // Ajout de C2_SERVER_URL aux dépendances de useCallback
    
    React.useEffect(() => {
        // Charger les agents si la vue active est 'agents', 'dashboard', ou 'graph'
        // Car le graphe a aussi besoin des données agents.
        if (activeView === 'agents' || activeView === 'dashboard' || activeView === 'graph') {
            fetchAgents();
        }
    }, [activeView, fetchAgents]); // fetchAgents ajouté aux dépendances

    let currentViewComponent;
    switch (activeView) {
        case 'dashboard':
            currentViewComponent = React.createElement(DashboardView, { agents: agents, error: loadingError, onRefresh: fetchAgents });
            break;
        case 'agents':
            currentViewComponent = React.createElement(AgentsListView, { agents: agents, error: loadingError, onRefresh: fetchAgents });
            break;
        case 'graph':
            // Passer les agents au AdGraphView
            currentViewComponent = React.createElement(AdGraphView, { agents: agents, error: loadingError });
            break;
        default:
            currentViewComponent = React.createElement('div', null, 'Vue non trouvée');
    }

    return (
        React.createElement(React.Fragment, null,
            React.createElement(Header, { activeView: activeView, setActiveView: setActiveView }),
            React.createElement('main', { className: "main-content" },
                currentViewComponent
            ),
            React.createElement(Footer, null)
        )
    );
};

// --- Render the App ---
const rootElement = document.getElementById('root');
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(React.createElement(App, null));
} else {
    console.error("L'élément racine 'root' est introuvable dans le DOM.");
} 