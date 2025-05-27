// import React, { useState, useEffect } from 'react'; // Supprimé

const AgentsListView = ({ agents, error, onRefresh }) => {
    const getStatusClass = (status) => {
        switch (status) {
            case 'ACTIVE': return 'status-active';
            case 'INACTIVE': return 'status-inactive';
            case 'PENDING': return 'status-pending';
            default: return 'status-unknown';
        }
    };
    
    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleString(undefined, { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return dateString; 
        }
    };

    const getOsIcon = (osString) => {
        if (!osString) return React.createElement('span', { title: "OS Inconnu" }, "❓");
        const os = osString.toLowerCase();
        if (os.includes('windows')) return React.createElement('span', { title: osString }, "🪟"); // Windows icon
        if (os.includes('linux')) return React.createElement('span', { title: osString }, "🐧"); // Linux icon
        if (os.includes('macos') || os.includes('darwin')) return React.createElement('span', { title: osString }, "🍏"); // macOS icon
        return React.createElement('span', { title: osString }, "💻"); // Generic computer icon
    };

    // Pour la future sélection multiple (fictif pour l'instant)
    const [selectedAgents, setSelectedAgents] = React.useState([]); 
    const handleSelectAgent = (agentId) => {
        // Logique de sélection à implémenter
        alert(`Sélection/désélection de l'agent ${agentId} (logique à venir)`);
    };

    return (
        React.createElement('div', null,
            React.createElement('div', { className: "view-header" },
                React.createElement('h1', null, 
                    React.createElement('span', {role: "img", "aria-label": "agents"}, "👥"), 
                    ` Liste des Agents (${agents.length})`
                ),
                React.createElement('div', { className: "actions-toolbar" },
                    React.createElement('button', { onClick: onRefresh }, 
                        React.createElement('span', {role: "img", "aria-label": "refresh"}, "🔄"), 
                        " Rafraîchir"
                    ),
                    React.createElement('button', { 
                        onClick: () => alert('Fonctionnalité "Envoyer Commande" à venir.'), 
                        disabled: selectedAgents.length === 0 
                    }, 
                        React.createElement('span', {role: "img", "aria-label": "command"}, "⚙️"), 
                        " Envoyer Commande"
                    ),
                    React.createElement('button', { 
                        onClick: () => alert('Fonctionnalité "Planifier Tâche" à venir.'), 
                        disabled: selectedAgents.length === 0 
                    }, 
                        React.createElement('span', {role: "img", "aria-label": "task"}, "📅"), 
                        " Planifier Tâche"
                    )
                )
            ),
            error && React.createElement('p', { className: "error-message" }, error),
            !error && agents.length === 0 && React.createElement('p', { className: "loading-message" }, `Aucun agent enregistré ou chargement en cours... Le serveur C2 est-il bien lancé et accessible sur ${C2_SERVER_URL}?`),
            agents.length > 0 && (
                React.createElement('table', { className: "agents-table stylish-table" },
                    React.createElement('thead', null,
                        React.createElement('tr', null,
                            React.createElement('th', null, "Statut"),
                            React.createElement('th', null, "OS"),
                            React.createElement('th', null, "ID Agent"),
                            React.createElement('th', null, "Hostname"),
                            React.createElement('th', null, "IP Interne"),
                            React.createElement('th', null, "Utilisateur"),
                            React.createElement('th', null, "Premier Contact"),
                            React.createElement('th', null, "Dernier Check-in"),
                            React.createElement('th', null, "Version Agent")
                        )
                    ),
                    React.createElement('tbody', null,
                        agents.map(agent => (
                            React.createElement('tr', { key: agent.id, className: selectedAgents.includes(agent.id) ? 'selected-row' : '' },
                                React.createElement('td', null, React.createElement('span', { className: `status-icon ${getStatusClass(agent.status)}`, title: agent.status })), 
                                React.createElement('td', { className: "os-icon-cell" }, getOsIcon(agent.os_target)),
                                React.createElement('td', { title: agent.id }, agent.id.length > 15 ? agent.id.substring(0,12) + '...' : agent.id),
                                React.createElement('td', null, agent.hostname || 'N/A'),
                                React.createElement('td', null, agent.internal_ip || 'N/A'),
                                React.createElement('td', null, agent.username || 'N/A'),
                                React.createElement('td', null, formatDate(agent.first_seen)),
                                React.createElement('td', { className: new Date() - new Date(agent.last_checkin_time) > 60000 * 5 ? 'last-checkin-late' : '' }, formatDate(agent.last_checkin_time)),
                                React.createElement('td', null, agent.agent_version || 'N/A')
                            )
                        ))
                    )
                )
            ),
            agents.length > 5 && React.createElement('p', {style: {textAlign: 'center', marginTop: '15px', fontSize: '0.9em', color: '#aaa'}}, "Note: La pagination sera implémentée pour un grand nombre d'agents.")
        )
    );
};

// export default AgentsListView; // Supprimé 