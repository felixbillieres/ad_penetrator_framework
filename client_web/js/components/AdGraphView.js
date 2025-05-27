// import React, { useState, useRef, useEffect, Fragment } from 'react'; // Supprimé
// import cytoscape from 'cytoscape'; // Supprimé, cytoscape est global

const AdGraphView = ({ agents, error: propError }) => {
    const [selectedElement, setSelectedElement] = React.useState(null);
    const cyRef = React.useRef(null);
    const [graphError, setGraphError] = React.useState(null);
    const [cytoscapeElements, setCytoscapeElements] = React.useState([]);
    const [ownedNodes, setOwnedNodes] = React.useState(new Set()); // Pour marquer les noeuds "owned"

    const toggleNodeOwned = (nodeId) => {
        setOwnedNodes(prevOwnedNodes => {
            const newOwnedNodes = new Set(prevOwnedNodes);
            if (newOwnedNodes.has(nodeId)) {
                newOwnedNodes.delete(nodeId);
            } else {
                newOwnedNodes.add(nodeId);
            }
            // Mettre à jour le style du noeud dans Cytoscape
            if (cyRef.current) {
                const node = cyRef.current.getElementById(nodeId);
                if (node) {
                    if (newOwnedNodes.has(nodeId)) {
                        node.addClass('owned');
                    } else {
                        node.removeClass('owned');
                    }
                }
            }
            return newOwnedNodes;
        });
    };

    const transformAgentsToCytoscapeElements = (agentsData) => {
        if (!agentsData || agentsData.length === 0) {
            return [];
        }

        const elements = [];
        const nodeIds = new Set();

        agentsData.forEach(agent => {
            const machineId = `machine-${agent.id}`;
            if (!nodeIds.has(machineId)) {
                elements.push({
                    data: {
                        id: machineId,
                        label: agent.hostname || agent.id.substring(0, 8),
                        type: 'Machine',
                        raw_data: agent,
                        owned: ownedNodes.has(machineId) // Ajout état owned
                    }
                });
                nodeIds.add(machineId);
            }

            let domainId = null;
            if (agent.domain_name && agent.domain_name.toUpperCase() !== 'WORKGROUP' && agent.domain_name.trim() !== "") {
                domainId = `domain-${agent.domain_name.toLowerCase()}`;
                if (!nodeIds.has(domainId)) {
                    elements.push({
                        data: {
                            id: domainId,
                            label: agent.domain_name,
                            type: 'Domain',
                            raw_data: { name: agent.domain_name, type: 'Domain' },
                            owned: ownedNodes.has(domainId)
                        }
                    });
                    nodeIds.add(domainId);
                }
                elements.push({ data: { id: `edge-${machineId}-${domainId}`, source: machineId, target: domainId, label: 'joined_to' } });
            }

            if (agent.current_user) {
                const userName = agent.current_user;
                const isDomainUser = domainId && agent.domain_name && agent.domain_name.toUpperCase() !== 'WORKGROUP' && agent.domain_name.trim() !== "";
                const userScope = isDomainUser ? agent.domain_name.toLowerCase() : machineId; // Utilisateur de domaine ou local à la machine
                const userId = `user-${userName.toLowerCase()}@${userScope}`;
                
                if (!nodeIds.has(userId)) {
                    elements.push({
                        data: {
                            id: userId,
                            label: userName,
                            type: isDomainUser ? 'DomainUser' : 'LocalUser', // LocalUser s'il n'est pas explicitement de domaine lié à CETTE machine
                            raw_data: { 
                                username: userName, 
                                domain: isDomainUser ? agent.domain_name : null,
                                on_machine: agent.hostname || agent.id, // Contexte de la machine où cet utilisateur est "current"
                                privileges: agent.current_user_privileges,
                                type: isDomainUser ? 'DomainUser' : 'LocalUser',
                            },
                            owned: ownedNodes.has(userId)
                        }
                    });
                    nodeIds.add(userId);
                }
                elements.push({ data: { id: `edge-${machineId}-${userId}-runs`, source: machineId, target: userId, label: 'runs_as' } });
                
                if (isDomainUser && domainId) { // S'il est utilisateur de domaine ET que le domaine existe
                     elements.push({ data: { id: `edge-${userId}-${domainId}-memberof`, source: userId, target: domainId, label: 'domain_member' } });
                }
            }
            
            if (agent.local_users && Array.isArray(agent.local_users)) {
                agent.local_users.forEach(localUserName => {
                    if (!localUserName || localUserName.trim() === "") return;
                    // ID unique pour un utilisateur local sur une machine spécifique
                    const localUserId = `localuser-${localUserName.toLowerCase()}@${machineId}`;
                    if (!nodeIds.has(localUserId)) {
                        const isLocalAdmin = agent.local_admins && agent.local_admins.map(admin => admin.toLowerCase()).includes(localUserName.toLowerCase());
                        elements.push({
                            data: {
                                id: localUserId,
                                label: localUserName,
                                type: 'LocalUserOnMachine',
                                raw_data: {
                                    username: localUserName,
                                    on_machine_id: machineId,
                                    on_machine_hostname: agent.hostname || agent.id,
                                    is_local_admin: isLocalAdmin,
                                    type: 'LocalUserOnMachine'
                                },
                                owned: ownedNodes.has(localUserId)
                            }
                        });
                        nodeIds.add(localUserId);
                    }
                    elements.push({ data: { id: `edge-${machineId}-${localUserId}-haslocal`, source: machineId, target: localUserId, label: 'has_local_user' } });
                });
            }
        });
        return elements;
    };

    React.useEffect(() => {
        if (propError) {
            setGraphError(propError);
            if(cyRef.current) {
                cyRef.current.destroy();
                cyRef.current = null;
            }
            return;
        }
        setGraphError(null);
        const newElements = transformAgentsToCytoscapeElements(agents);
        // Appliquer l'état 'owned' aux nouveaux éléments
        const elementsWithOwnedStatus = newElements.map(el => {
            if (el.data && ownedNodes.has(el.data.id)) {
                return { ...el, classes: 'owned' }; // Cytoscape utilise 'classes' pour appliquer des styles via sélecteurs
            }
            return el;
        });
        setCytoscapeElements(elementsWithOwnedStatus);
    }, [agents, propError, ownedNodes]); // ownedNodes ajouté comme dépendance


    React.useEffect(() => {
        console.log("AdGraphView: useEffect pour initialisation Cytoscape déclenché.");
        const container = document.getElementById('cy-container');
        if (!container) {
            console.error("AdGraphView: Erreur critique - Le conteneur #cy-container est INTROUVABLE.");
            setGraphError("Erreur critique: Le conteneur du graphe est manquant.");
            return;
        }

        // Vérifier UNIQUEMENT cytoscape global
        if (typeof window.cytoscape === 'undefined') {
            console.error("AdGraphView: Erreur critique - Cytoscape (window.cytoscape) n'est pas chargé.");
            setGraphError("Erreur critique: La librairie Cytoscape principale (window.cytoscape) est manquante.");
            return;
        }

        if (cytoscapeElements.length === 0 && !propError && agents && agents.length > 0) {
            console.log("AdGraphView: En attente des éléments Cytoscape ou données agents vides (mais agents existent).");
            if(cyRef.current) {
                cyRef.current.destroy();
                cyRef.current = null;
            }
            return;
        }
        
        if (cytoscapeElements.length === 0 && (!agents || agents.length === 0) && !propError) {
             console.log("AdGraphView: Pas de données agents à afficher, graphe vide.");
              if(cyRef.current) {
                cyRef.current.destroy();
                cyRef.current = null;
            }
        }

        console.log("AdGraphView: Initialisation de Cytoscape avec les éléments:", cytoscapeElements);

        try {
            if(cyRef.current) {
                cyRef.current.destroy();
            }

            const cyInstance = cytoscape({
                container: container,
                elements: cytoscapeElements, 
                style: [
                    { selector: 'node', style: { 'label': 'data(label)', 'width': '80px', 'height': '80px', 'text-valign': 'bottom', 'text-halign': 'center', 'font-size': '10px', 'color': '#fff', 'text-outline-width': 1, 'text-outline-color': '#333', 'border-width': 2, 'border-color': '#555' } },
                    { selector: 'edge', style: { 'width': 2, 'line-color': '#6c757d', 'target-arrow-color': '#6c757d', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '8px', 'color': '#bbb', 'text-rotation': 'autorotate', 'text-background-opacity': 0.7, 'text-background-color': '#222', 'text-background-padding': '2px'} },
                    { selector: 'node[type="Machine"]', style: { 'background-color': '#0D6EFD', 'shape': 'rectangle', 'border-color': '#0a58ca' } },
                    { selector: 'node[type="DomainUser"]', style: { 'background-color': '#198754', 'shape': 'ellipse', 'border-color': '#146c43' } },
                    { selector: 'node[type="LocalUser"]', style: { 'background-color': '#6C757D', 'shape': 'ellipse', 'border-color': '#5a6268' } }, 
                    { selector: 'node[type="LocalUserOnMachine"]', style: { 'background-color': '#ADB5BD', 'shape': 'ellipse', 'width': '60px', 'height': '60px', 'border-color': '#919ca3' } },
                    { selector: 'node[type="Domain"]', style: { 'background-color': '#FFC107', 'shape': 'round-diamond', 'width': '100px', 'height': '70px', 'border-color': '#d39e00' } },
                    { selector: 'node.owned', style: { 
                        'border-color': '#FF0000', 
                        'border-width': 4,
                        'overlay-color': '#FF0000',
                        'overlay-padding': '6px',
                        'overlay-opacity': 0.3
                    }},
                    { selector: 'edge[label="joined_to"]', style: {'line-style': 'dashed'} },
                    { selector: 'edge[label="has_local_user"]', style: {'line-color': '#adb5bd', 'target-arrow-color': '#adb5bd'} },
                    { selector: '.path-highlight', style: { 'background-color': 'red', 'line-color': 'red', 'target-arrow-color': 'red', 'width': 4, 'z-index': 9999 } }
                ],
                layout: {
                    name: 'cose', // CHANGÉ pour 'cose'
                    animate: true,
                    animationDuration: 1000,
                    fit: true,
                    padding: 50,
                    nodeRepulsion: function( node ){
                        // Augmenter la répulsion pour les noeuds de type 'Domain' pour mieux les espacer
                        return node.data('type') === 'Domain' ? 200000 : 100000;
                    },
                    idealEdgeLength: function( edge ){
                        // Augmenter la longueur idéale des arêtes connectées à un 'Domain'
                        return edge.source().data('type') === 'Domain' || edge.target().data('type') === 'Domain' ? 150 : 80;
                    },
                    nodeOverlap: 20, // Permettre un peu plus de chevauchement si nécessaire
                    gravity: 80, // Augmenter la gravité pour rapprocher les composants déconnectés
                    numIter: 1000,
                    initialTemp: 200,
                    coolingFactor: 0.95,
                    minTemp: 1.0
                }
            });
            console.log("AdGraphView: Instance Cytoscape créée avec layout 'cose'.", cyInstance);

            cyInstance.on('tap', 'node, edge', (event) => {
                const targetData = event.target.data();
                if (!targetData.type && event.target.isEdge()) {
                    targetData.type = 'Relation';
                    targetData.sourceNode = cyInstance.getElementById(targetData.source).data();
                    targetData.targetNode = cyInstance.getElementById(targetData.target).data();
                }
                setSelectedElement(targetData);
            });
            cyInstance.on('tap', (event) => {
                if (event.target === cyInstance) { 
                    setSelectedElement(null); 
                }
            });
            
            cyRef.current = cyInstance;
            setGraphError(null);
            console.log("AdGraphView: Graphe initialisé et écouteurs attachés.");

            // Appliquer la classe 'owned' aux noeuds déjà marqués lors de l'init (au cas où les éléments sont recréés)
            ownedNodes.forEach(nodeId => {
                const node = cyInstance.getElementById(nodeId);
                if(node) node.addClass('owned');
            });

            const resizeObserver = new ResizeObserver(() => {
                if(cyRef.current && container) {
                    cyRef.current.resize();
                    cyRef.current.fit(null, 50); // Augmenter le padding au fit
                }
            });
            resizeObserver.observe(container);

            return () => {
                console.log("AdGraphView: Nettoyage de useEffect - destruction.");
                if(container) resizeObserver.unobserve(container);
                if(cyRef.current) {
                     cyRef.current.destroy();
                     cyRef.current = null;
                }
            };
        } catch (e) {
            console.error("AdGraphView: ERREUR lors de l'initialisation de Cytoscape:", e);
            setGraphError(`Erreur Cytoscape: ${e.message}`);
        }

    }, [cytoscapeElements]); // Dépendance sur cytoscapeElements uniquement pour la recréation du graphe.

    const findExploitPaths = (targetNodeId) => {
        if (!cyRef.current || !selectedElement || !selectedElement.id || !targetNodeId) {
            alert("Sélectionnez un nœud source et une cible valide pour la recherche de chemin.");
            return;
        }
        const cy = cyRef.current;
        const sourceId = selectedElement.id;
        
        cy.elements().removeClass('path-highlight').deselect();

        const aStar = cy.elements().aStar({ 
            root: `#${sourceId}`, 
            goal: `#${targetNodeId}`,
            weight: edge => {
                // Exemple de poids, à affiner
                if (edge.data('label') === 'runs_as') return 1;
                if (edge.data('label') === 'joined_to') return 5; // Plus coûteux de sauter de machine à domaine
                if (edge.data('label') === 'domain_member') return 0.5; // Facile si on est déjà user du domaine
                if (edge.data('label') === 'has_local_user') return 2;
                return 3; 
            }
        });

        if (aStar.found) {
            aStar.path.addClass('path-highlight');
            aStar.path.select();
            const pathNodes = aStar.path.nodes().map(n => n.data('label')).join(' -> ');
            const pathEdges = aStar.path.edges().map(e => e.data('label') || 'related').join(', ');
            setTimeout(() => alert(`Chemin trouvé (coût: ${aStar.distance.toFixed(1)}):
Nœuds: ${pathNodes}
Via: ${pathEdges}`), 100);
        } else {
            const sourceLabel = cy.$(`#${sourceId}`).data('label');
            const targetLabel = cy.$(`#${targetNodeId}`).data('label');
            alert(`Aucun chemin direct trouvé de ${sourceLabel} à ${targetLabel} avec la configuration actuelle.`);
        }
    };

    const recenterGraph = () => {
        if(cyRef.current && cyRef.current.elements().length > 0) {
            cyRef.current.animate({
                fit: { eles: cyRef.current.elements(), padding: 50 },
                duration: 500
            });
        }
    };
    
    const exportGraphPNG = () => {
        if(cyRef.current && cyRef.current.elements().length > 0){
            try {
                const png64 = cyRef.current.png({output: 'base64', full:true, scale: 2, bg: '#21252b'});
                const link = document.createElement('a');
                link.href = 'data:image/png;base64,' + png64;
                link.download = 'ad_penetrator_graph.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            } catch (e) {
                console.error("Erreur export PNG:", e);
                alert("Erreur lors de l'exportation en PNG.");
            }
        } else {
            alert("Le graphe est vide, rien à exporter.")
        }
    };

    if (graphError && graphError !== propError) {
        return (
            React.createElement('div', { className: "ad-graph-view-container error-container" },
                React.createElement('h3', null, "Erreur Graphe AD"),
                React.createElement('p', { className: "error-message" }, graphError),
                React.createElement('p', null, "Vérifiez la console du navigateur (F12).")
            )
        );
    }
    
    if (propError) {
         return (
            React.createElement('div', { className: "ad-graph-view-container error-container" },
                React.createElement('h3', null, "Erreur de Données pour le Graphe AD"),
                React.createElement('p', { className: "error-message" }, propError),
                React.createElement('p', null, "Impossible de charger les données des agents pour construire le graphe.")
            )
        );
    }


    return (
        React.createElement(React.Fragment, null,
            React.createElement('div', { className: "graph-controls", style: { paddingBottom: '15px', borderBottom: '1px solid #444', marginBottom: '15px', display: 'flex', gap: '10px', flexWrap: 'wrap' } },
                React.createElement('button', { onClick: recenterGraph, title: "Recentrer le graphe" }, "Recentrer Graphe"),
                React.createElement('button', { onClick: exportGraphPNG, title: "Exporter en PNG" }, "Exporter en PNG")
            ),
            React.createElement('div', { className: "ad-graph-view-container" },
                React.createElement('div', { id: "cy-container", style: { flexGrow: 1, minHeight: '600px' } }),
                React.createElement(GraphInfoPanel, { 
                    node: selectedElement, 
                    onFindPath: findExploitPaths, 
                    allNodes: cyRef.current ? cyRef.current.nodes().map(n => n.data()) : [],
                    toggleNodeOwned: toggleNodeOwned, // Passer la fonction pour marquer "owned"
                    ownedNodeIds: ownedNodes // Passer l'ensemble des IDs owned
                })
            )
        )
    );
};

// export default AdGraphView; 