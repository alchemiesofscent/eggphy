document.addEventListener('DOMContentLoaded', async () => {

    const familyRoots = [
        { id: 'A_Classical', name: 'Family A: Classical & Renaissance Tradition', desc: 'The full gall-ink recipe, with a soak-then-boil process. The archetypes.' },
        { id: 'B_LongSoak', name: "Family B: The 'Long-Soak' Lineage", desc: 'Innovation 1: Galls are dropped, but a slow multi-day soak is required.' },
        { id: 'G_Cepak', name: "Family G: Cépak's Modernized Hybrid", desc: 'Innovation 2: Precise quantities are added to the gall-less, long-soak recipe.' },
        { id: 'D_SaltWaterBoil', name: "Family D: The 'Salt-Water-Boil' Lineage", desc: 'Parallel Innovation: The process is simplified to a direct salt water boil.' },
        { id: 'C_Modern', name: "Family C: The 'Modern Baby' (Recombination)", desc: 'The final synthesis: No galls, no soak, and precise quantities.' },
        { id: 'F_Anomalous', name: "Family F: Anomalous 'Boil-Then-Write' Tradition", desc: 'A separate branch where the process is reversed. Egg is boiled before writing.' },
        { id: 'E_Meta', name: 'Family E: Meta-Witnesses & Outliers', desc: 'Witnesses that test, analyze, or exist outside the main tradition.' }
    ];

    // Load witness data from the main data file
    let witnessData = [];
    try {
        const dataUrl = new URL('../data/witnesses.json', window.location.href).href;
        const response = await fetch('../data/witnesses.json');
        if (response.ok) {
            witnessData = await response.json();
        } else {
            console.error('Stemma Family View: Failed to load witness data:', response.status, response.statusText);
            // Fallback to empty array
            witnessData = [];
        }
    } catch (error) {
        console.error('Error loading witness data:', error);
        // Try to load from API as fallback
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

    // Use shared classifier to keep logic unified
    const classifyWitness = (w) => (window._classifyRecipe && window._classifyRecipe(w)) || 'E_Meta';

    // --- Main Application Logic (Unchanged from before) ---

    // 1. Group the data
    const groupedWitnesses = {};
    familyRoots.forEach(family => groupedWitnesses[family.id] = []);
    
    witnessData.forEach(witness => {
        const familyId = classifyWitness(witness);
        if (groupedWitnesses[familyId]) {
            groupedWitnesses[familyId].push(witness);
        }
    });

    // Sort witnesses within each group by date
    for (const familyId in groupedWitnesses) {
        groupedWitnesses[familyId].sort((a, b) => a.metadata.date - b.metadata.date);
    }
    
    // 2. Render the application structure
    const rootsContainer = document.getElementById('family-roots-container');
    const displayContainer = document.getElementById('witness-display-container');

    // Render root buttons
    familyRoots.forEach(family => {
        const rootEl = document.createElement('div');
        rootEl.className = 'family-root';
        rootEl.dataset.familyId = family.id;
        rootEl.setAttribute('data-family-id', family.id); // For CSS styling
        rootEl.innerHTML = `
            <h2>${family.name} (${groupedWitnesses[family.id].length})</h2>
            <p>${family.desc}</p>
        `;
        rootsContainer.appendChild(rootEl);
    });

    // Render witness groups (initially hidden)
    for (const familyId in groupedWitnesses) {
        const groupEl = document.createElement('div');
        groupEl.id = `family-${familyId}-witnesses`;
        groupEl.className = 'witness-group hidden';
        
        groupedWitnesses[familyId].forEach(witness => {
            const cardEl = document.createElement('div');
            cardEl.className = 'witness-card';

            // Create a more informative summary
            const gallPresence = witness.ingredients?.diagnostic_variants?.gall_presence || 'unknown';
            const boilingTiming = witness.process_steps?.critical_variants?.boiling_timing || 'unknown';
            const soakingDuration = witness.process_steps?.critical_variants?.soaking_duration || 'unknown';

            let summary = `Galls: ${gallPresence}`;
            if (boilingTiming !== 'unknown') summary += `, Boiling: ${boilingTiming.replace('_', ' ')}`;
            if (soakingDuration !== 'unknown') summary += `, Soaking: ${soakingDuration}`;

            const author = witness.metadata?.author || 'Unknown author';
            const language = witness.metadata?.language || 'unknown';
            const source = witness.metadata?.source_work || 'Unknown source';

            cardEl.innerHTML = `
                <h3><a href="../recipe.html?id=${witness.metadata?.witness_id}&from=stemma" style="color: inherit; text-decoration: none;">${witness.metadata?.witness_id || 'Unknown'} (${witness.metadata?.date || 'Unknown date'})</a></h3>
                <p><strong>Author:</strong> ${author}</p>
                <p><strong>Language:</strong> ${language.toUpperCase()}</p>
                <p><strong>Source:</strong> ${source}</p>
                <p><strong>Process Summary:</strong> ${summary}</p>
                <details>
                    <summary>Show Full Data</summary>
                    <pre>${JSON.stringify(witness, null, 2)}</pre>
                </details>
            `;
            groupEl.appendChild(cardEl);
        });
        displayContainer.appendChild(groupEl);
    }

    // 3. Add event listeners
    rootsContainer.addEventListener('click', (e) => {
        const clickedRoot = e.target.closest('.family-root');
        if (!clickedRoot) return;

        const familyId = clickedRoot.dataset.familyId;

        // Toggle active class on roots
        document.querySelectorAll('.family-root').forEach(root => root.classList.remove('active'));
        clickedRoot.classList.add('active');
        
        // Show/hide the correct witness group
        document.querySelectorAll('.witness-group').forEach(group => group.classList.add('hidden'));
        const targetGroup = document.getElementById(`family-${familyId}-witnesses`);
        if (targetGroup) {
            targetGroup.classList.remove('hidden');
        }
    });
});
