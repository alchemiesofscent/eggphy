document.addEventListener('DOMContentLoaded', async () => {

    // Load witness data from the main data file
    let witnessData = [];
    try {
        const response = await fetch('../../data/witnesses.json');
        if (response.ok) {
            witnessData = await response.json();
        } else {
            console.error('Failed to load witness data:', response.status);
            witnessData = [];
        }
    } catch (error) {
        console.error('Error loading witness data:', error);
        try {
            const apiResponse = await fetch('/api/witnesses');
            if (apiResponse.ok) {
                witnessData = await apiResponse.json();
            }
        } catch (apiError) {
            console.error('API fallback also failed:', apiError);
            witnessData = [];
        }
    }

    // Function to classify a witness into a family (same as original stemma)
    function classifyWitness(witness) {
        const id = witness.metadata?.witness_id;
        const ingredients = witness.ingredients?.diagnostic_variants;
        const process = witness.process_steps?.critical_variants;

        if (!id || !ingredients || !process) {
            return 'E_Meta';
        }

        // Handle outliers first
        if (['W23', 'W27', 'W37', 'W74', 'W87'].includes(id)) return 'E_Meta';
        if (process.boiling_timing === 'before_writing') return 'F_Anomalous';
        if (id === 'W57') return 'G_Cepak';

        // Main classifications
        const hasSaltWaterBoil = witness.process_steps?.preparation_sequence?.some(s =>
            s.details && (s.details.toLowerCase().includes('salt water') || s.details.toLowerCase().includes('salzwasser'))
        ) || false;

        if (ingredients.gall_presence === 'present' && process.soaking_duration !== 'days' && hasSaltWaterBoil) {
            return 'D_SaltWaterBoil';
        }
        if (ingredients.gall_presence === 'absent' && process.soaking_duration === 'days') {
            return 'B_LongSoak';
        }
        if (ingredients.gall_presence === 'absent' && process.soaking_duration !== 'days') {
            return 'C_Modern';
        }
        if (ingredients.gall_presence === 'present') {
            return 'A_Classical';
        }

        return 'E_Meta';
    }

    // Group witnesses by family
    const familyGroups = {
        'A_Classical': [],
        'B_LongSoak': [],
        'C_Modern': [],
        'D_SaltWaterBoil': [],
        'E_Meta': [],
        'F_Anomalous': [],
        'G_Cepak': []
    };

    witnessData.forEach(witness => {
        const family = classifyWitness(witness);
        if (familyGroups[family]) {
            familyGroups[family].push(witness);
        }
    });

    // Sort witnesses by date within each family
    Object.keys(familyGroups).forEach(family => {
        familyGroups[family].sort((a, b) => (a.metadata?.date || 0) - (b.metadata?.date || 0));
    });

    // View switching functionality
    const treeViewBtn = document.getElementById('treeViewBtn');
    const timelineViewBtn = document.getElementById('timelineViewBtn');
    const treeView = document.getElementById('tree-view');
    const timelineView = document.getElementById('timeline-view');
    const detailsPanel = document.getElementById('witness-details');

    let currentView = 'tree';

    function switchView(view) {
        currentView = view;

        if (view === 'tree') {
            treeViewBtn.classList.add('active');
            timelineViewBtn.classList.remove('active');
            treeView.classList.remove('hidden');
            timelineView.classList.add('hidden');
        } else {
            timelineViewBtn.classList.add('active');
            treeViewBtn.classList.remove('active');
            timelineView.classList.remove('hidden');
            treeView.classList.add('hidden');
        }
    }

    treeViewBtn.addEventListener('click', () => switchView('tree'));
    timelineViewBtn.addEventListener('click', () => switchView('timeline'));

    // Timeline zoom functionality
    let currentZoom = 1.0;
    let timelineStart = 1000;
    let timelineEnd = 2025;

    function updateTimelineZoom() {
        const timelineContent = document.querySelector('.timeline-content');
        const timelineContainer = document.querySelector('.timeline-container');
        const zoomLevel = document.getElementById('zoom-level');
        const markers = document.querySelectorAll('.century-marker');

        if (!timelineContainer || markers.length === 0) return;

        // Calculate how many markers we have
        const yearRange = timelineEnd - timelineStart;
        const markerInterval = yearRange > 500 ? 100 : 50;
        const markerCount = Math.ceil(yearRange / markerInterval) + 1;

        // Get the actual container width (excluding family label width and scrollbar)
        const containerWidth = timelineContainer.clientWidth;
        const familyLabelWidth = 180; // matches CSS .family-label width
        const availableWidth = containerWidth - familyLabelWidth - 20; // 20px for padding/margins

        // Calculate base marker width to fit container at 100% zoom
        const baseMarkerWidth = Math.max(availableWidth / markerCount, 80); // minimum 80px per marker

        // Calculate expanded width based on zoom
        const expandedWidth = baseMarkerWidth * currentZoom;

        // Always set explicit width for proper horizontal scrolling
        const totalWidth = markerCount * expandedWidth;
        timelineContent.style.width = `${totalWidth}px`;

        // Update individual marker widths
        markers.forEach(marker => {
            marker.style.minWidth = `${expandedWidth}px`;
            marker.style.flexBasis = `${expandedWidth}px`;
        });

        zoomLevel.textContent = `${Math.round(currentZoom * 100)}%`;
    }

    function updateTimelineRange() {
        const startLabel = document.getElementById('start-year-label');
        const endLabel = document.getElementById('end-year-label');

        startLabel.textContent = timelineStart;
        endLabel.textContent = timelineEnd;

        // Re-render timeline with new range
        renderTimelineView();
        updateTimelineZoom();
    }

    // Zoom controls
    document.getElementById('zoom-in')?.addEventListener('click', () => {
        currentZoom = Math.min(currentZoom * 1.25, 5.0);
        updateTimelineZoom();
    });

    document.getElementById('zoom-out')?.addEventListener('click', () => {
        currentZoom = Math.max(currentZoom / 1.25, 0.25);
        updateTimelineZoom();
    });

    document.getElementById('zoom-reset')?.addEventListener('click', () => {
        currentZoom = 1.0;
        updateTimelineZoom();
    });

    // Time range controls
    document.getElementById('start-year')?.addEventListener('input', (e) => {
        timelineStart = parseInt(e.target.value);
        const endInput = document.getElementById('end-year');
        if (timelineStart >= timelineEnd) {
            timelineEnd = timelineStart + 100;
            endInput.value = timelineEnd;
        }
        updateTimelineRange();
    });

    document.getElementById('end-year')?.addEventListener('input', (e) => {
        timelineEnd = parseInt(e.target.value);
        const startInput = document.getElementById('start-year');
        if (timelineEnd <= timelineStart) {
            timelineStart = timelineEnd - 100;
            startInput.value = timelineStart;
        }
        updateTimelineRange();
    });

    // Family information
    const familyInfo = {
        'A_Classical': { name: 'Family A: Classical & Renaissance', desc: 'Gall + Alum Tradition', symbol: 'α' },
        'B_LongSoak': { name: 'Family B: Long-Soak Lineage', desc: 'Multi-day soaking innovation', symbol: 'β' },
        'C_Modern': { name: 'Family C: Modern Baby', desc: 'No galls, no long soak', symbol: 'γ' },
        'D_SaltWaterBoil': { name: 'Family D: Salt-Water-Boil', desc: 'Direct salt water process', symbol: 'δ' },
        'E_Meta': { name: 'Family E: Meta-Witnesses', desc: 'Outliers and commentary', symbol: 'ε' },
        'F_Anomalous': { name: 'Family F: Anomalous Branch', desc: 'Boil-then-write tradition', symbol: 'ζ' },
        'G_Cepak': { name: 'Family G: Cépak Hybrid', desc: 'Quantified long-soak', symbol: 'η' }
    };

    const familyColorMap = {
        'A_Classical': 'var(--family-a)',
        'B_LongSoak': 'var(--family-b)',
        'C_Modern': 'var(--family-c)',
        'D_SaltWaterBoil': 'var(--family-d)',
        'E_Meta': 'var(--family-e)',
        'F_Anomalous': 'var(--family-f)',
        'G_Cepak': 'var(--family-g)'
    };

    // Build and render the collapsible tree
    function renderCollapsibleTree() {
        const archetype = document.querySelector('[data-node-id="archetype"]');
        const familyContainer = archetype.querySelector('.children-nodes');

        // Update archetype count
        const archetypeCount = archetype.querySelector('.node-count');
        const totalFamilies = Object.keys(familyInfo).length;
        archetypeCount.textContent = `(${totalFamilies} families)`;

        // Clear existing content
        familyContainer.innerHTML = '';

        // Create family nodes - include all families even if empty for now
        Object.entries(familyInfo).forEach(([familyId, familyData]) => {
            const witnesses = familyGroups[familyId] || [];

            const familyNode = document.createElement('div');
            familyNode.className = 'tree-node family-node';
            familyNode.dataset.nodeId = familyId;
            familyNode.dataset.family = familyId;
            familyNode.dataset.expanded = 'false';

            familyNode.innerHTML = `
                <div class="node-content">
                    <div class="expand-indicator">▶</div>
                    <div class="node-info">
                        <h4>${familyData.symbol} ${familyData.name}</h4>
                        <p>${familyData.desc}</p>
                        <span class="node-count">(${witnesses.length} witnesses)</span>
                    </div>
                </div>
                <div class="children-container">
                    <svg class="connection-svg"></svg>
                    <div class="children-nodes">
                        ${witnesses.length > 0 ? renderWitnessNodes(witnesses, familyId) : '<div class="no-witnesses">No witnesses in this family</div>'}
                    </div>
                </div>
            `;

            // Ensure children are hidden initially
            const childrenContainer = familyNode.querySelector('.children-container');
            const childrenNodes = familyNode.querySelector('.children-nodes');
            childrenContainer.style.maxHeight = '0';
            childrenNodes.style.opacity = '0';
            childrenNodes.style.visibility = 'hidden';

            // Add click handler for expand/collapse
            const nodeContent = familyNode.querySelector('.node-content');
            nodeContent.addEventListener('click', (e) => {
                e.stopPropagation();
                toggleNode(familyNode);
            });

            familyContainer.appendChild(familyNode);
        });

        // Add click handler for archetype node
        const archetypeContent = archetype.querySelector('.node-content');
        archetypeContent.addEventListener('click', (e) => {
            e.stopPropagation();
            toggleNode(archetype);
        });

        // Ensure archetype starts collapsed
        const archetypeContainer = archetype.querySelector('.children-container');
        const archetypeNodes = archetype.querySelector('.children-nodes');
        archetypeContainer.style.maxHeight = '0';
        archetypeNodes.style.opacity = '0';
        archetypeNodes.style.visibility = 'hidden';

        // Draw connection lines after all nodes are created
        drawConnectionLines();
    }

    // Function to draw connection lines between nodes
    function drawConnectionLines() {
        // Draw lines from archetype to families when expanded
        const archetype = document.querySelector('[data-node-id="archetype"]');
        if (archetype && archetype.dataset.expanded === 'true') {
            drawLinesFromParent(archetype);
        }

        // Draw lines from families to witnesses when expanded
        document.querySelectorAll('.family-node[data-expanded="true"]').forEach(familyNode => {
            drawLinesFromParent(familyNode);
        });
    }

    // Function to draw lines from a parent to its children
    function drawLinesFromParent(parentNode) {
        const svg = parentNode.querySelector('.connection-svg');
        const childrenNodes = parentNode.querySelector('.children-nodes');

        if (!svg || !childrenNodes) return;

        // Clear existing lines
        svg.innerHTML = '';

        const children = childrenNodes.querySelectorAll('.tree-node');
        if (children.length === 0) return;

        // Calculate positions
        const parentWidth = parentNode.querySelector('.node-content').offsetWidth;
        const startX = parentWidth / 2;
        const startY = 0;

        children.forEach((child, index) => {
            const childRect = child.getBoundingClientRect();
            const parentRect = parentNode.getBoundingClientRect();
            const relativeX = childRect.left - parentRect.left + childRect.width / 2;
            const relativeY = 40; // Fixed height from parent

            // Create SVG line
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', startX);
            line.setAttribute('y1', startY);
            line.setAttribute('x2', relativeX);
            line.setAttribute('y2', relativeY);
            line.setAttribute('class', 'connection-line');

            svg.appendChild(line);
        });
    }

    // Render witness nodes for a family
    function renderWitnessNodes(witnesses, familyId) {
        return witnesses.map(witness => {
            const witnessId = witness.metadata?.witness_id || 'Unknown';
            const date = witness.metadata?.date || 'Unknown';
            const sourceWork = witness.metadata?.source_work || 'Unknown Source';

            return `
                <div class="tree-node witness-node" data-witness-id="${witnessId}">
                    <div class="node-content">
                        <div class="node-info" onclick="showWitnessDetails(event, '${witnessId}')">
                            <div class="family-indicator" style="background: ${familyColorMap[familyId]}"></div>
                            <h5>${sourceWork}</h5>
                            <p class="date">${date}</p>
                            <p class="witness-id">Witness ID: ${witnessId}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    // Toggle node expansion
    function toggleNode(node) {
        const isExpanded = node.dataset.expanded === 'true';
        node.dataset.expanded = !isExpanded;

        const indicator = node.querySelector('.expand-indicator');
        const container = node.querySelector('.children-container');
        const childrenNodes = node.querySelector('.children-nodes');

        if (!isExpanded) {
            // Expanding
            indicator.style.transform = 'rotate(90deg)';
            indicator.style.background = 'var(--accent)';
            indicator.style.color = 'white';

            // Show children with CSS classes (let CSS handle the animation)
            container.style.maxHeight = '3000px';
            container.style.padding = '20px 0 0 0';
            childrenNodes.style.opacity = '1';
            childrenNodes.style.visibility = 'visible';
        } else {
            // Collapsing
            indicator.style.transform = 'rotate(0deg)';
            indicator.style.background = 'var(--surface)';
            indicator.style.color = 'var(--accent)';

            // Hide children
            container.style.maxHeight = '0';
            container.style.padding = '0';
            childrenNodes.style.opacity = '0';
            childrenNodes.style.visibility = 'hidden';
        }

        // Redraw connection lines after a short delay to allow animation
        setTimeout(() => {
            drawConnectionLines();
        }, 50);
    }

    // Show witness details (modified to work with the new structure)
    window.showWitnessDetails = function(event, witnessId) {
        if (event) event.stopPropagation();

        const witness = witnessData.find(w => w.metadata?.witness_id === witnessId);
        if (!witness) return;

        const panel = document.getElementById('witness-details');
        const title = document.getElementById('details-title');
        const content = document.getElementById('details-content');

        title.textContent = `${witness.metadata?.witness_id || 'Unknown'} (${witness.metadata?.date || 'Unknown'})`;

        const gallPresence = witness.ingredients?.diagnostic_variants?.gall_presence || 'unknown';
        const boilingTiming = witness.process_steps?.critical_variants?.boiling_timing || 'unknown';
        const soakingDuration = witness.process_steps?.critical_variants?.soaking_duration || 'unknown';
        const soakingMedium = witness.process_steps?.critical_variants?.soaking_medium || 'unknown';

        content.innerHTML = `
            <p><strong>Author:</strong> ${witness.metadata?.author || 'Unknown'}</p>
            <p><strong>Language:</strong> ${(witness.metadata?.language || 'unknown').toUpperCase()}</p>
            <p><strong>Source:</strong> ${witness.metadata?.source_work || 'Unknown'}</p>
            <p><strong>Gall Presence:</strong> ${gallPresence}</p>
            <p><strong>Boiling Timing:</strong> ${boilingTiming.replace('_', ' ')}</p>
            <p><strong>Soaking Duration:</strong> ${soakingDuration}</p>
            <p><strong>Soaking Medium:</strong> ${soakingMedium}</p>
            <p><strong>Family:</strong> ${classifyWitness(witness).replace('_', ' ')}</p>

            ${witness.ingredients?.primary_components ? `
                <p><strong>Ingredients:</strong></p>
                <ul style="margin: 8px 0 16px 20px; font-size: 0.85rem;">
                    ${witness.ingredients.primary_components.map(comp =>
                        `<li>${comp.substance}${comp.quantity ? ` (${comp.quantity})` : ''}</li>`
                    ).join('')}
                </ul>
            ` : ''}

            ${witness.process_steps?.preparation_sequence ? `
                <p><strong>Process Steps:</strong></p>
                <ol style="margin: 8px 0 16px 20px; font-size: 0.85rem;">
                    ${witness.process_steps.preparation_sequence.slice(0, 3).map(step =>
                        `<li>${step.action}: ${step.details}</li>`
                    ).join('')}
                    ${witness.process_steps.preparation_sequence.length > 3 ? '<li>...</li>' : ''}
                </ol>
            ` : ''}
        `;

        panel.classList.remove('hidden');
    };

    // Render Timeline View
    function renderTimelineView() {
        // Update century markers
        const timelineScale = document.querySelector('.timeline-scale');
        timelineScale.innerHTML = '';

        const yearRange = timelineEnd - timelineStart;
        const markerInterval = yearRange > 500 ? 100 : 50;

        for (let year = timelineStart; year <= timelineEnd; year += markerInterval) {
            const marker = document.createElement('div');
            marker.className = 'century-marker';
            marker.textContent = `${year} CE`;
            timelineScale.appendChild(marker);
        }

        // Render witnesses
        Object.entries(familyGroups).forEach(([familyId, witnesses]) => {
            const trackId = `timeline-family-${familyId.charAt(0)}`;
            const track = document.getElementById(trackId);

            if (!track) return;

            track.innerHTML = '';

            witnesses.forEach(witness => {
                const date = witness.metadata?.date || timelineStart;

                // Only show witnesses within the current time range
                if (date < timelineStart || date > timelineEnd) return;

                // Calculate position based on current time range
                const position = ((date - timelineStart) / (timelineEnd - timelineStart)) * 100;

                const dot = document.createElement('div');
                dot.className = `timeline-witness family-${familyId.charAt(0)}`;
                dot.style.left = `${Math.max(0, Math.min(100, position))}%`;
                dot.dataset.witnessId = witness.metadata?.witness_id;
                dot.title = `${witness.metadata?.witness_id} (${date})`;

                dot.addEventListener('click', () => {
                    window.showWitnessDetails(null, witness.metadata?.witness_id);
                });
                track.appendChild(dot);
            });
        });
    }

    // Show witness details in panel
    function showWitnessDetails(witness) {
        const panel = document.getElementById('witness-details');
        const title = document.getElementById('details-title');
        const content = document.getElementById('details-content');

        title.textContent = `${witness.metadata?.witness_id || 'Unknown'} (${witness.metadata?.date || 'Unknown'})`;

        const gallPresence = witness.ingredients?.diagnostic_variants?.gall_presence || 'unknown';
        const boilingTiming = witness.process_steps?.critical_variants?.boiling_timing || 'unknown';
        const soakingDuration = witness.process_steps?.critical_variants?.soaking_duration || 'unknown';
        const soakingMedium = witness.process_steps?.critical_variants?.soaking_medium || 'unknown';

        content.innerHTML = `
            <p><strong>Author:</strong> ${witness.metadata?.author || 'Unknown'}</p>
            <p><strong>Language:</strong> ${(witness.metadata?.language || 'unknown').toUpperCase()}</p>
            <p><strong>Source:</strong> ${witness.metadata?.source_work || 'Unknown'}</p>
            <p><strong>Gall Presence:</strong> ${gallPresence}</p>
            <p><strong>Boiling Timing:</strong> ${boilingTiming.replace('_', ' ')}</p>
            <p><strong>Soaking Duration:</strong> ${soakingDuration}</p>
            <p><strong>Soaking Medium:</strong> ${soakingMedium}</p>
            <p><strong>Family:</strong> ${classifyWitness(witness).replace('_', ' ')}</p>

            ${witness.ingredients?.primary_components ? `
                <p><strong>Ingredients:</strong></p>
                <ul style="margin: 8px 0 16px 20px; font-size: 0.85rem;">
                    ${witness.ingredients.primary_components.map(comp =>
                        `<li>${comp.substance}${comp.quantity ? ` (${comp.quantity})` : ''}</li>`
                    ).join('')}
                </ul>
            ` : ''}

            ${witness.process_steps?.preparation_sequence ? `
                <p><strong>Process Steps:</strong></p>
                <ol style="margin: 8px 0 16px 20px; font-size: 0.85rem;">
                    ${witness.process_steps.preparation_sequence.slice(0, 3).map(step =>
                        `<li>${step.action}: ${step.details}</li>`
                    ).join('')}
                    ${witness.process_steps.preparation_sequence.length > 3 ? '<li>...</li>' : ''}
                </ol>
            ` : ''}
        `;

        panel.classList.remove('hidden');
    }

    // Close details panel
    document.getElementById('close-details').addEventListener('click', () => {
        document.getElementById('witness-details').classList.add('hidden');
    });

    // Close panel when clicking outside
    document.addEventListener('click', (e) => {
        const panel = document.getElementById('witness-details');
        if (!panel.contains(e.target) && !e.target.closest('.witness-node') && !e.target.closest('.timeline-witness')) {
            panel.classList.add('hidden');
        }
    });

    // Initialize views
    renderCollapsibleTree();
    renderTimelineView();

    // Wait for DOM to be fully ready before calculating timeline zoom
    setTimeout(() => {
        updateTimelineZoom();
    }, 100);

    // Add some demo data if no real data is loaded
    if (witnessData.length === 0) {
        console.warn('No witness data loaded, adding demo data for visualization');

        // Create some demo witnesses for visualization
        const demoWitnesses = [
            {
                metadata: { witness_id: 'W01', date: 1000, author: 'Geoponica', language: 'grk', source_work: 'Geoponikon' },
                ingredients: { diagnostic_variants: { gall_presence: 'present' } },
                process_steps: { critical_variants: { boiling_timing: 'after_writing', soaking_duration: 'unspecified' } }
            },
            {
                metadata: { witness_id: 'W15', date: 1300, author: 'Medieval Source', language: 'lat', source_work: 'Unknown' },
                ingredients: { diagnostic_variants: { gall_presence: 'absent' } },
                process_steps: { critical_variants: { boiling_timing: 'after_writing', soaking_duration: 'days' } }
            },
            {
                metadata: { witness_id: 'W45', date: 1650, author: 'Early Modern', language: 'deu', source_work: 'German Manual' },
                ingredients: { diagnostic_variants: { gall_presence: 'absent' } },
                process_steps: { critical_variants: { boiling_timing: 'after_writing', soaking_duration: 'hours' } }
            }
        ];

        witnessData = demoWitnesses;

        // Re-populate with demo data
        Object.keys(familyGroups).forEach(key => familyGroups[key] = []);
        witnessData.forEach(witness => {
            const family = classifyWitness(witness);
            if (familyGroups[family]) {
                familyGroups[family].push(witness);
            }
        });

        renderCollapsibleTree();
        renderTimelineView();
        setTimeout(() => {
            updateTimelineZoom();
        }, 100);
    }
});