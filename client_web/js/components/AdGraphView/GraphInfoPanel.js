// import React, { useState, useEffect } from 'react'; // Supprimé

const GraphInfoPanel = ({ node, onFindPath, allNodes, toggleNodeOwned, ownedNodeIds }) => {
    if (!node) {
        return (
            React.createElement('div', {id: "info-panel"},
                React.createElement('h2', null, "Explorateur de Graphe AD"),
                React.createElement('p', null, "Cliquez sur un nœud (machine, utilisateur, domaine) ou une relation pour afficher ses détails."),
                React.createElement('p', null, "Zoomez/Dézoomez avec la molette. Déplacez le graphe en cliquant et glissant sur le fond."),
                React.createElement('p', null, "Utilisez les données des agents récupérées pour construire le graphe.")
            )
        );
    }

    const [targetNodeForPath, setTargetNodeForPath] = React.useState(""); 
    const nodeData = node.raw_data || node;
    const nodeId = node.id; // ID Cytoscape
    const nodeType = node.type;

    const computerNodesForSelect = allNodes ? allNodes.filter(n => n.type === 'Machine' && n.id !== nodeId) : [];

    let displayProperties = {};
    let title = node.label || nodeId;
    let subtitle = nodeType;
    let isOwnable = false; // Seuls certains types de noeuds peuvent être "owned"

    if (nodeType === 'Machine' && nodeData) {
        isOwnable = true;
        title = nodeData.hostname || node.label;
        subtitle = `Machine (Agent ID: ${nodeData.id ? nodeData.id.substring(0,8) : 'N/A'}... )`;
        displayProperties = {
            "ID Agent": nodeData.id,
            "Hostname": nodeData.hostname,
            "IP Interne": nodeData.internal_ip,
            "Utilisateur Actuel": nodeData.current_user,
            "Privilèges Utilisateur": nodeData.current_user_privileges,
            "OS Cible": nodeData.os_target,
            "Version Agent": nodeData.agent_version,
            "Architecture": nodeData.architecture,
            "Processeur": nodeData.processor,
            "Nom de Domaine": nodeData.domain_name,
            "Utilisateurs Locaux": nodeData.local_users ? nodeData.local_users.join(', ') : 'N/A',
            "Admins Locaux": nodeData.local_admins ? nodeData.local_admins.join(', ') : 'N/A',
            "Premier Contact": nodeData.first_seen ? new Date(nodeData.first_seen).toLocaleString() : 'N/A',
            "Dernier Check-in": nodeData.last_checkin_time ? new Date(nodeData.last_checkin_time).toLocaleString() : 'N/A',
        };
    } else if ((nodeType === 'DomainUser' || nodeType === 'LocalUser') && nodeData) {
        isOwnable = true;
        title = nodeData.username || node.label;
        subtitle = nodeType === 'DomainUser' ? `Utilisateur de Domaine (${nodeData.domain || 'N/A'})` : `Utilisateur (${nodeData.on_machine || 'Contexte local' })`;
        displayProperties = {
            "Nom d'utilisateur": nodeData.username,
            "Type d'utilisateur": nodeData.type, // 'DomainUser' ou 'LocalUser'
            "Domaine": nodeData.domain || 'N/A (Local au contexte machine)',
            "Contexte Machine": nodeData.on_machine || 'N/A',
            "Privilèges (si agent)": nodeData.privileges || 'N/A',
        };
    } else if (nodeType === 'LocalUserOnMachine' && nodeData) {
        isOwnable = true; // On peut marquer un compte local spécifique comme owned
        title = nodeData.username || node.label;
        subtitle = `Compte Local sur ${nodeData.on_machine_hostname}`;
        displayProperties = {
            "Nom d'utilisateur": nodeData.username,
            "Sur Machine": nodeData.on_machine_hostname,
            "Est Admin Local": nodeData.is_local_admin ? 'Oui' : 'Non',
        };
    } else if (nodeType === 'Domain' && nodeData) {
        isOwnable = true; // On peut marquer un domaine comme compromis
        title = nodeData.name || node.label;
        subtitle = 'Domaine Active Directory';
        displayProperties = { "Nom de Domaine": nodeData.name };
    } else if (nodeType === 'Relation' && nodeData) {
        title = nodeData.label || 'Relation';
        subtitle = `De: ${nodeData.sourceNode?.label || nodeData.source} \nVers: ${nodeData.targetNode?.label || nodeData.target}`;
        displayProperties = {
            "Type": nodeData.label || 'Inconnu',
            "Source ID": nodeData.source,
            "Cible ID": nodeData.target,
            "Source Label": nodeData.sourceNode?.label,
            "Cible Label": nodeData.targetNode?.label,
        };
    }

    const handleOwnedChange = (e) => {
        if (nodeId && toggleNodeOwned) {
            toggleNodeOwned(nodeId);
        }
    };

    let exploitActions = [];
    if (nodeType === 'DomainUser' || nodeType === 'LocalUser' || nodeType === 'LocalUserOnMachine') {
        exploitActions.push({ label: `Kerberoast ${title}`, category: 'Exploitation', action: () => alert(`[Fictif] Kerberoasting sur ${title}`) });
        if (nodeData && nodeData.privileges === 'Admin') {
             exploitActions.push({ label: `DCSync (via ${title})`, category: 'Exploitation', action: () => alert(`[Fictif] Tentative de DCSync en utilisant les droits de ${title}...`) });
        }
    }
    if (nodeType === 'Machine') {
        exploitActions.push({ label: `Scanner ports sur ${title}`, category: 'Reconnaissance', action: () => alert(`[Fictif] Scan des ports sur ${title}`) });
        if (nodeData && (nodeData.os_target?.toLowerCase().includes('server') || nodeData.hostname?.toLowerCase().includes('dc'))) {
             exploitActions.push({ label: `Scan Vulns DC/Serveur (${title})`, category: 'Reconnaissance', action: () => alert(`[Fictif] Scan de vulnérabilités spécifiques aux serveurs sur ${title}...`) });
        }
         exploitActions.push({ label: `Récupérer NTDS.dit de ${title} (si DC)`, category: 'Credential Access', action: () => alert(`[Fictif] Tentative de récupération de NTDS.dit depuis ${title}...`) });
    }

    const categorizedActions = exploitActions.reduce((acc, action) => {
        const category = action.category || 'Général';
        if (!acc[category]) acc[category] = [];
        acc[category].push(action);
        return acc;
    }, {});

    return (
        React.createElement('div', {id: "info-panel"},
            React.createElement('h2', null, title, 
                React.createElement('span', {className: "node-type-badge", style: { marginLeft: '10px'}}, subtitle)
            ),
            
            isOwnable && toggleNodeOwned && ownedNodeIds && React.createElement('div', { style: { margin: '10px 0', padding: '8px', backgroundColor:'#333', borderRadius:'4px'} },
                React.createElement('label', {
                    htmlFor: `owned-checkbox-${nodeId}`,
                    style: { cursor: 'pointer', display: 'flex', alignItems: 'center'}
                },
                    React.createElement('input', {
                        type: 'checkbox',
                        id: `owned-checkbox-${nodeId}`,
                        checked: ownedNodeIds.has(nodeId),
                        onChange: handleOwnedChange,
                        style: { marginRight: '8px', transform: 'scale(1.2)' }
                    }),
                    React.createElement('span', {style:{fontWeight: ownedNodeIds.has(nodeId) ? 'bold' : 'normal', color: ownedNodeIds.has(nodeId) ? '#ff4d4d' : 'inherit'}}, "Marquer comme 'Owned'")
                )
            ),

            Object.keys(displayProperties).length > 0 && (
                React.createElement(React.Fragment, null,
                    React.createElement('h3', {className: "info-panel-subtitle"}, "Détails de l'élément:"),
                    React.createElement('table', {className: "node-details-table"},
                        React.createElement('tbody', null,
                            Object.entries(displayProperties).map(([key, value]) => (
                                (value !== undefined && value !== null && String(value).trim() !== '') && React.createElement('tr', {key: key},
                                    React.createElement('th', null, key),
                                    React.createElement('td', null, String(value))
                                )
                            ))
                        )
                    )
                )
            ),

            Object.keys(categorizedActions).length > 0 && (
                 React.createElement(React.Fragment, null,
                    React.createElement('h3', {className: "info-panel-subtitle with-margin"}, "Actions / Scénarios (Fictifs):"),
                    Object.entries(categorizedActions).map(([category, actions]) => (
                        React.createElement('div', {key: category, className: "action-category"},
                            React.createElement('h4', null, category),
                            React.createElement('div', {className: "exploit-actions-container"},
                                actions.map((actionItem, index) => (
                                    React.createElement('button', {
                                        key: index,
                                        onClick: actionItem.action, 
                                        title: actionItem.label,
                                        className: `exploit-button ${actionItem.type === 'path' ? 'path-finding' : ''}`
                                    },
                                    actionItem.label.length > 40 ? actionItem.label.substring(0,37)+"..." : actionItem.label
                                    )
                                ))
                            )
                        )
                    ))
                 )
            ),
            
            (nodeType === 'DomainUser' || nodeType === 'LocalUser' || nodeType === 'Machine' || nodeType === 'LocalUserOnMachine') && computerNodesForSelect.length > 0 && 
            React.createElement('div', { className: 'pathfinding-controls', style: { marginTop: '20px', paddingTop: '15px', borderTop: '1px solid #555'} },
                React.createElement('h4', {style:{color: '#61dafb'}}, "Recherche de Chemin d'Exploitation"),
                React.createElement('p', {style:{fontSize: '0.9em', marginBottom: '10px'}}, `Depuis ${title} (type: ${nodeType}) vers un ordinateur cible :`),
                React.createElement('label', { htmlFor: 'target-node-select-gip', style:{marginRight: '5px'} }, "Cible: "),
                React.createElement('select', { 
                    id: 'target-node-select-gip',
                    value: targetNodeForPath, 
                    onChange: e => setTargetNodeForPath(e.target.value), 
                    style: { marginRight: '10px', padding: '5px', backgroundColor: '#333', color:'white', border:'1px solid #555' }
                },
                    React.createElement('option', { value: "" }, "-- Choisir un ordinateur --"),
                    computerNodesForSelect.map(cn => React.createElement('option', { key: cn.id, value: cn.id }, cn.label || cn.id))
                ),
                React.createElement('button', { 
                    onClick: () => { if(targetNodeForPath) onFindPath(targetNodeForPath); else alert("Veuillez choisir une cible."); }, 
                    disabled: !targetNodeForPath, 
                    style: {padding: '5px 10px'}
                }, "Trouver Chemin")
            )
        )
    );
}; 