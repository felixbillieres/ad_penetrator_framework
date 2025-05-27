// import React, { useState, useEffect } from 'react'; // Supprimé

const DashboardView = ({ agents, error, onRefresh }) => {
    const activeAgents = agents.filter(agent => agent.status === 'ACTIVE');
    const inactiveAgents = agents.filter(agent => agent.status !== 'ACTIVE');
    const totalAgents = agents.length;

    const osTypes = agents.reduce((acc, agent) => {
        const os = agent.os_target || "Inconnu";
        acc[os] = (acc[os] || 0) + 1;
        return acc;
    }, {});

    // Données fictives pour nouvelles cartes
    const tasksInProgress = 5;
    const tasksCompleted = 22;
    const criticalVulnerabilities = 3;
    const recentActivities = [
        { id: 1, time: "10:45", text: "Agent WORKSTATION-05 check-in." },
        { id: 2, time: "10:42", text: "Scan de vulnérabilités lancé sur SRV-DC01." },
        { id: 3, time: "10:30", text: "Nouvel agent ADMIN-PC enregistré." },
    ];

    const InfoTooltip = ({ text }) => (
        React.createElement('span', { className: "info-tooltip", title: text }, 'ⓘ')
    );

    return (
        React.createElement('div', null,
            React.createElement('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' } },
                React.createElement('h1', null, 'Tableau de Bord'),
                React.createElement('button', { onClick: onRefresh, style: { height: 'fit-content' } },
                    React.createElement('span', { role: "img", "aria-label": "refresh" }, '🔄'),
                    ' Rafraîchir les Données'
                )
            ),
            
            error && React.createElement('p', { className: "error-message" }, error),

            // Section Bienvenue et Aide
            React.createElement('div', { className: "dashboard-card help-card", style: { marginBottom: '20px' } },
                React.createElement('h2', null, 'Bienvenue sur AD Penetrator Web UI!'),
                React.createElement('p', null, 'Cette interface vous permet de visualiser et d\'interagir avec vos agents déployés et les données Active Directory collectées.'),
                React.createElement('ul', null,
                    React.createElement('li', null, React.createElement('strong', null, 'Dashboard:'), ' Vue d\'ensemble de l\'état du système et des agents.'),
                    React.createElement('li', null, React.createElement('strong', null, 'Agents:'), ' Liste détaillée de tous les agents, leur statut et informations.'),
                    React.createElement('li', null, React.createElement('strong', null, 'Graphe AD:'), ' Visualisation interactive des relations et objets AD (données fictives actuellement).')
                ),
                React.createElement('p', null, 'Utilisez la navigation en haut pour changer de vue. Les données du graphe AD sont pour l\'instant simulées.')
            ),
            
            React.createElement('div', { className: "dashboard-grid" },
                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { className: "status-icon status-active" }), 
                        'Agents Actifs ', 
                        React.createElement(InfoTooltip, { text: "Agents actuellement connectés et envoyant des beacons." })
                    ),
                    React.createElement('p', null, React.createElement('span', { className: "stat-value" }, activeAgents.length))
                ),
                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { className: "status-icon status-inactive" }), 
                        'Agents Inactifs/Autres ', 
                        React.createElement(InfoTooltip, { text: "Agents enregistrés mais non connectés récemment." })
                    ),
                    React.createElement('p', null, React.createElement('span', { className: "stat-value" }, inactiveAgents.length))
                ),
                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { className: "status-icon status-unknown" }), 
                        'Total Agents ', 
                        React.createElement(InfoTooltip, { text: "Nombre total d'agents uniques enregistrés." })
                    ),
                    React.createElement('p', null, React.createElement('span', { className: "stat-value" }, totalAgents))
                ),
                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "server" }, '📡'), 
                        ' État Serveur C2 ', 
                        React.createElement(InfoTooltip, { text: `Statut de la connexion à l'API du C2: ${C2_SERVER_URL}` })
                    ),
                    error && !agents.length ? 
                        React.createElement('p', { className: "status-text error" }, "NON CONNECTÉ") : 
                        React.createElement('p', { className: "status-text success" }, "CONNECTÉ"),
                    React.createElement('p', { style: { fontSize: '0.8em', color: '#aaa', textAlign: 'center' } }, C2_SERVER_URL)
                ),

                totalAgents > 0 && (
                    React.createElement('div', { className: "dashboard-card large-card" }, 
                        React.createElement('h2', null, 
                            React.createElement('span', { role: "img", "aria-label": "os" }, '💻'), 
                            ' Répartition des OS Agents'
                        ),
                        Object.keys(osTypes).length > 0 ? (
                            React.createElement('ul', { className: "os-list" },
                                Object.entries(osTypes).map(([os, count]) => (
                                    React.createElement('li', { key: os },
                                        React.createElement('span', null, os, ": "), 
                                        React.createElement('strong', null, count)
                                    )
                                ))
                            )
                        ) : (
                            React.createElement('p', null, "Aucune information d'OS disponible.")
                        )
                    )
                ),

                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "tasks" }, '📊'), 
                        ' Tâches ', 
                        React.createElement(InfoTooltip, { text: "Statut des tâches assignées aux agents (fictif)." })
                    ),
                    React.createElement('p', null, 'En cours: ', React.createElement('strong', { style: { color: '#61dafb' } }, tasksInProgress)),
                    React.createElement('p', null, 'Terminées: ', React.createElement('strong', { style: { color: '#8bc34a' } }, tasksCompleted)),
                    React.createElement('button', { style: { marginTop: '10px', fontSize: '0.9em', width: '100%' }, onClick: () => alert('Page de gestion des tâches (à venir)') }, 'Voir les Tâches')
                ),

                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "vuln" }, '⚠️'), 
                        ' Vulnérabilités Critiques ', 
                        React.createElement(InfoTooltip, { text: "Nombre de vulnérabilités critiques identifiées (fictif)." })
                    ),
                    React.createElement('p', null, React.createElement('span', { className: "stat-value alert" }, criticalVulnerabilities)),
                    React.createElement('button', { style: { marginTop: '10px', fontSize: '0.9em', width: '100%' }, onClick: () => alert('Page des vulnérabilités (à venir)') }, 'Analyser Vulnérabilités')
                ),
                
                React.createElement('div', { className: "dashboard-card large-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "logs" }, '📋'), 
                        ' Activités Récentes ', 
                        React.createElement(InfoTooltip, { text: "Log simplifié des dernières actions importantes (fictif)." })
                    ),
                    React.createElement('ul', { className: "activity-log" },
                        recentActivities.map(activity => (
                            React.createElement('li', { key: activity.id },
                                React.createElement('span', { className: "log-time" }, activity.time),
                                React.createElement('span', { className: "log-text" }, activity.text)
                            )
                        ))
                    )
                )
            )
        )
    );
};

// export default DashboardView; // Supprimé 