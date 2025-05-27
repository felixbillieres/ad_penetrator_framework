// import React, { useState, useEffect } from 'react'; // Supprimé

const DashboardView = ({ agents, error, onRefresh }) => {
    const activeAgents = agents.filter(agent => agent.status === 'ACTIVE');
    const inactiveAgents = agents.filter(agent => agent.status !== 'ACTIVE'); // Inclut PENDING, INACTIVE, etc.
    const totalAgents = agents.length;

    const osTypes = agents.reduce((acc, agent) => {
        const os = agent.os_target || "Inconnu";
        acc[os] = (acc[os] || 0) + 1;
        return acc;
    }, {});

    const agentsByDomain = agents.reduce((acc, agent) => {
        const domain = agent.domain_name && agent.domain_name.toUpperCase() !== 'WORKGROUP' && agent.domain_name.trim() !== "" ? agent.domain_name : "WORKGROUP/Non Joint";
        acc[domain] = (acc[domain] || 0) + 1;
        return acc;
    }, {});

    const privilegeCounts = agents.reduce((acc, agent) => {
        const priv = agent.current_user_privileges || "Inconnu";
        acc[priv] = (acc[priv] || 0) + 1;
        return acc;
    }, {});

    const discoveredUsersSet = new Set();
    agents.forEach(agent => {
        if (agent.local_users && Array.isArray(agent.local_users)) {
            agent.local_users.forEach(user => discoveredUsersSet.add(`${user}@${agent.hostname || agent.id.substring(0,8)}`));
        }
        if (agent.current_user) {
            const userContext = agent.domain_name && agent.domain_name.toUpperCase() !== 'WORKGROUP' ? agent.domain_name : (agent.hostname || agent.id.substring(0,8));
            discoveredUsersSet.add(`${agent.current_user}@${userContext}`);
        }
    });
    const totalDiscoveredUniqueUsers = discoveredUsersSet.size;

    // Données fictives pour sections non encore implémentées
    const tasksInProgress = 0; // Sera mis à jour quand les tâches seront gérées
    const tasksCompleted = 0; // Sera mis à jour
    const criticalVulnerabilities = 0; // Sera mis à jour

    // Génération des activités récentes dynamiques
    const generateRecentActivities = (agentsData) => {
        const activities = [];
        let activityId = 0;
        const now = new Date();

        if (!agentsData || agentsData.length === 0) {
            activities.push({ id: activityId++, time: now.toLocaleTimeString(), text: "En attente de données agents..."});
            return activities.slice(0, 5); // Limiter à 5 activités
        }
        
        // Tri des agents par dernier check-in (plus récent en premier)
        const sortedAgents = [...agentsData].sort((a, b) => {
            const timeA = a.last_checkin_time ? new Date(a.last_checkin_time) : new Date(0);
            const timeB = b.last_checkin_time ? new Date(b.last_checkin_time) : new Date(0);
            return timeB - timeA;
        });

        const discoveredDomains = new Set();
        
        sortedAgents.slice(0, 10).forEach(agent => { // Considérer les 10 agents les plus récents pour les logs
            const agentName = agent.hostname || `Agent ${agent.id.substring(0,8)}`;
            const checkinTime = agent.last_checkin_time ? new Date(agent.last_checkin_time).toLocaleTimeString() : "N/A";

            activities.push({ id: activityId++, time: checkinTime, text: `Agent ${agentName} check-in.`});

            if (agent.domain_name && agent.domain_name.toUpperCase() !== 'WORKGROUP' && !discoveredDomains.has(agent.domain_name)) {
                activities.push({ id: activityId++, time: checkinTime, text: `Domaine '${agent.domain_name}' découvert via ${agentName}.`});
                discoveredDomains.add(agent.domain_name);
            }

            if (agent.current_user_privileges === 'Admin') {
                activities.push({ id: activityId++, time: checkinTime, text: `ALERTE: L'agent ${agentName} (utilisateur ${agent.current_user}) s'exécute avec des privilèges Admin !`});
            }
            
            if (agent.local_admins && agent.local_admins.length > 3) { // Exemple d'une "alerte" simple
                 activities.push({ id: activityId++, time: checkinTime, text: `INFO: ${agentName} rapporte ${agent.local_admins.length} administrateurs locaux.`});
            }
        });
        
        if (activities.length === 0){
             activities.push({ id: activityId++, time: now.toLocaleTimeString(), text: "Aucune activité notable récente des agents."});
        }

        // S'assurer que les activités les plus récentes (basées sur leur 'id' qui est incrémental) sont en haut.
        // Ou trier par 'time' si les timestamps sont fiables et dans le bon ordre après génération.
        // Pour l'instant, on va juste inverser pour que les dernières ajoutées soient en haut.
        return activities.reverse().slice(0, 7); // Limiter aux 7 plus récentes
    };
    
    const recentActivities = generateRecentActivities(agents);


    const InfoTooltip = ({ text }) => (
        React.createElement('span', { className: "info-tooltip", title: text }, 'ⓘ')
    );

    return (
        React.createElement('div', null,
            React.createElement('div', { style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' } },
                React.createElement('h1', null, React.createElement('span', {role: "img", "aria-label": "dashboard"}, "📊 "), 'Tableau de Bord'),
                React.createElement('button', { onClick: onRefresh, style: { height: 'fit-content' } },
                    React.createElement('span', { role: "img", "aria-label": "refresh" }, '🔄'),
                    ' Rafraîchir les Données'
                )
            ),
            
            error && React.createElement('p', { className: "error-message" }, error),

            // Section Bienvenue et Aide
            React.createElement('div', { className: "dashboard-card help-card", style: { marginBottom: '20px' } },
                React.createElement('h2', null, "Bienvenue sur AD Penetrator Web UI!"),
                React.createElement('p', null, "Cette interface vous permet de visualiser et d'interagir avec vos agents déployés et les données Active Directory collectées."),
                React.createElement('ul', null,
                    React.createElement('li', null, React.createElement('strong', null, "Dashboard:"), " Vue d'ensemble de l'état du système et des agents."),
                    React.createElement('li', null, React.createElement('strong', null, "Agents:"), " Liste détaillée de tous les agents, leur statut et informations."),
                    React.createElement('li', null, React.createElement('strong', null, "Graphe AD:"), " Visualisation interactive des relations et objets AD.")
                )
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
                        React.createElement(InfoTooltip, { text: "Agents enregistrés mais non connectés récemment, ou en attente." })
                    ),
                    React.createElement('p', null, React.createElement('span', { className: "stat-value" }, inactiveAgents.length))
                ),
                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "total-agents"}, "💻" ),
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
                        React.createElement('p', { className: "status-text error" }, "ERREUR CONNEXION") : 
                        React.createElement('p', { className: "status-text success" }, "CONNECTÉ"),
                    React.createElement('p', { style: { fontSize: '0.8em', color: '#aaa', textAlign: 'center', wordBreak: 'break-all' } }, C2_SERVER_URL)
                ),

                totalAgents > 0 && (
                    React.createElement('div', { className: "dashboard-card large-card" }, 
                        React.createElement('h2', null, 
                            React.createElement('span', { role: "img", "aria-label": "os" }, '🖥️'), 
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

                totalAgents > 0 && Object.keys(agentsByDomain).length > 0 && (
                    React.createElement('div', { className: "dashboard-card large-card" }, 
                        React.createElement('h2', null, 
                            React.createElement('span', { role: "img", "aria-label": "domain" }, '🌐'), 
                            ' Agents par Domaine/Workgroup'
                        ),
                        React.createElement('ul', { className: "os-list" },
                            Object.entries(agentsByDomain).map(([domain, count]) => (
                                React.createElement('li', { key: domain },
                                    React.createElement('span', null, domain, ": "), 
                                    React.createElement('strong', null, count)
                                )
                            ))
                        )
                    )
                ),

                totalAgents > 0 && Object.keys(privilegeCounts).length > 0 && (
                    React.createElement('div', { className: "dashboard-card" },
                        React.createElement('h2', null,
                            React.createElement('span', { role: "img", "aria-label": "privileges" }, '🛡️'),
                            ' Privilèges Agents ',
                            React.createElement(InfoTooltip, { text: "Répartition des privilèges des utilisateurs exécutant les agents." })
                        ),
                        Object.entries(privilegeCounts).map(([priv, count]) => (
                            React.createElement('p', { key: priv, style: { margin: '5px 0'} },
                                React.createElement('span', null, priv === 'Admin' ? '👑 Admin' : (priv === 'User' ? '👤 Utilisateur' : '❓ Inconnu'), ": "),
                                React.createElement('strong', null, count)
                            )
                        ))
                    )
                ),

                totalAgents > 0 && (
                     React.createElement('div', { className: "dashboard-card" },
                        React.createElement('h2', null,
                            React.createElement('span', { role: "img", "aria-label": "users" }, '👥'),
                            ' Utilisateurs Découverts ',
                            React.createElement(InfoTooltip, { text: "Nombre total d'utilisateurs uniques découverts (locaux et contexte agent) sur tous les agents." })
                        ),
                        React.createElement('p', null, React.createElement('span', { className: "stat-value" }, totalDiscoveredUniqueUsers))
                    )
                ),

                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "tasks" }, '⚙️'), // Changed icon
                        ' Tâches (Bientôt) ', 
                        React.createElement(InfoTooltip, { text: "Statut des tâches assignées aux agents." })
                    ),
                    React.createElement('p', null, 'En cours: ', React.createElement('strong', { style: { color: '#61dafb' } }, tasksInProgress)),
                    React.createElement('p', null, 'Terminées: ', React.createElement('strong', { style: { color: '#8bc34a' } }, tasksCompleted)),
                    React.createElement('button', { style: { marginTop: '10px', fontSize: '0.9em', width: '100%', backgroundColor: '#4a4f57', cursor:'not-allowed' }, disabled: true }, 'Gérer les Tâches')
                ),

                React.createElement('div', { className: "dashboard-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "vuln" }, '⚠️'), 
                        ' Vulnérabilités (Bientôt) ', 
                        React.createElement(InfoTooltip, { text: "Nombre de vulnérabilités critiques identifiées." })
                    ),
                    React.createElement('p', null, React.createElement('span', { className: "stat-value alert" }, criticalVulnerabilities)),
                    React.createElement('button', { style: { marginTop: '10px', fontSize: '0.9em', width: '100%', backgroundColor: '#4a4f57', cursor:'not-allowed' }, disabled: true }, 'Analyser Vulnérabilités')
                ),
                
                React.createElement('div', { className: "dashboard-card large-card" },
                    React.createElement('h2', null, 
                        React.createElement('span', { role: "img", "aria-label": "logs" }, '📋'), 
                        ' Activités Récentes ', 
                        React.createElement(InfoTooltip, { text: "Log simplifié des dernières actions importantes." })
                    ),
                    recentActivities.length > 0 ? (
                        React.createElement('ul', { className: "activity-log" },
                            recentActivities.map(activity => (
                                React.createElement('li', { key: activity.id },
                                    React.createElement('span', { className: "log-time" }, activity.time),
                                    React.createElement('span', { className: "log-text" }, activity.text)
                                )
                            ))
                        )
                    ) : (
                        React.createElement('p', { style: { fontStyle: 'italic', color: '#aaa'}}, "Aucune activité récente à afficher.")
                    )
                )
            )
        )
    );
};

// export default DashboardView; // Supprimé 