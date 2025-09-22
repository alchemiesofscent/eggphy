        let recipes = [];
        let filteredRecipes = [];
        let currentIndex = -1;
        const selected = {
            centuries: new Set(),
            languages: new Set(),
            genres: new Set(),
            ingredientFamily: new Set(),
            ingredients: new Set(),
            boil: new Set(),
            dry: new Set(),
            soakMedium: new Set(),
            soakDuration: new Set(),
        };

        function renderSkeleton(n=8) {
            const grid = document.getElementById('recipeGrid');
            grid.innerHTML = Array.from({length:n}).map(()=>`
                <div class="skeleton-card">
                    <div class="skeleton-line lg"></div>
                    <div class="skeleton-line md"></div>
                    <div class="skeleton-line sm"></div>
                </div>
            `).join('');
        }

        function groupMap(key) {
            switch(key){
                case 'cent': return 'centuries';
                case 'lang': return 'languages';
                case 'genre': return 'genres';
                case 'ingredientFamily': return 'ingredientFamily';
                case 'ingredient': return 'ingredients';
                case 'boil': return 'boil';
                case 'dry': return 'dry';
                case 'soakMedium': return 'soakMedium';
                case 'soakDuration': return 'soakDuration';
            }
            return key;
        }

        function renderCheckboxList(containerId, items, prefix) {
            const el = document.getElementById(containerId);
            el.innerHTML = items.map((it) => `
                <label class="checkbox-item">
                    <input type="checkbox" data-group="${prefix}" value="${it.value}"> ${it.label}
                </label>
            `).join('');
            el.addEventListener('change', (e) => {
                const t = e.target;
                if (t && t.matches('input[type="checkbox"][data-group]')) {
                    const group = t.getAttribute('data-group');
                    const set = selected[groupMap(group)];
                    if (t.checked) set.add(t.value); else set.delete(t.value);
                    updateFilterCount(prefix);
                    applyFilters();
                }
            });
        }

        function updateFilterCount(prefix) {
            const group = groupMap(prefix);
            const count = selected[group].size;
            const idPrefixMap = { cent: 'century', lang: 'language' };
            const countEl = document.getElementById((idPrefixMap[prefix] || prefix) + 'Count');
            if (countEl) {
                countEl.textContent = count === 0 ? '(0 selected)' : `(${count} selected)`;
            }
        }

        function getIngredientFamily(recipe) {
            // Check if recipe has galls and alum
            let hasGalls = false;
            let hasAlum = false;

            // Check from the simplified ingredients array (used by the original interface)
            if (Array.isArray(recipe.ingredients)) {
                hasGalls = recipe.ingredients.some(ing => ing.toLowerCase().includes('gall'));
                hasAlum = recipe.ingredients.some(ing => ing.toLowerCase().includes('alum'));
            }

            // Also check from the detailed JSON structure if available
            const detailedIngredients = recipe.full_data && recipe.full_data.ingredients;
            if (detailedIngredients && detailedIngredients.diagnostic_variants) {
                if (detailedIngredients.diagnostic_variants.gall_presence === 'present') {
                    hasGalls = true;
                }
            }

            // Check primary_components in detailed structure
            if (detailedIngredients && Array.isArray(detailedIngredients.primary_components)) {
                detailedIngredients.primary_components.forEach(comp => {
                    if (comp.substance && comp.substance.toLowerCase().includes('gall')) {
                        hasGalls = true;
                    }
                    if (comp.substance && comp.substance.toLowerCase().includes('alum')) {
                        hasAlum = true;
                    }
                });
            }

            if (hasGalls && hasAlum) {
                return 'Gall and Alum Family';
            } else if (hasAlum && !hasGalls) {
                return 'Alum Only Family';
            } else {
                return 'Other';
            }
        }

        function setupFilterToggles() {
            document.querySelectorAll('.filter-toggle').forEach(toggle => {
                const handleToggle = (e) => {
                    e.stopPropagation();

                    const targetId = toggle.getAttribute('data-target');
                    const contentId = targetId.replace('List', 'Content');
                    const content = document.getElementById(contentId);

                    if (content) {
                        const isExpanded = toggle.classList.contains('expanded');

                        // Close all other filters
                        document.querySelectorAll('.filter-toggle').forEach(t => {
                            t.classList.remove('expanded');
                            t.setAttribute('aria-expanded', 'false');
                        });
                        document.querySelectorAll('.filter-content').forEach(c => {
                            c.classList.remove('expanded');
                            c.setAttribute('hidden', '');
                        });

                        // Toggle current filter
                        if (!isExpanded) {
                            toggle.classList.add('expanded');
                            toggle.setAttribute('aria-expanded', 'true');
                            content.classList.add('expanded');
                            content.removeAttribute('hidden');
                        } else {
                            toggle.classList.remove('expanded');
                            toggle.setAttribute('aria-expanded', 'false');
                            content.classList.remove('expanded');
                            content.setAttribute('hidden', '');
                        }
                    }
                };

                toggle.addEventListener('click', handleToggle);
            });
        }

        function navigate(delta) {
            if (!filteredRecipes.length) return;
            if (currentIndex === -1) currentIndex = 0;
            currentIndex = (currentIndex + delta + filteredRecipes.length) % filteredRecipes.length;
            const nextId = filteredRecipes[currentIndex].witness_id;
            showDetails(nextId);
        }

        function initThemeAndFont() {
            // Delegate theme setup to shared theme.js if available
            if (typeof window.initTheme === 'function') {
                window.initTheme();
            }
            if (typeof window.updateThemeToggleIcon === 'function') {
                window.updateThemeToggleIcon();
            }
            // Apply saved font scale
            const savedScale = parseFloat(localStorage.getItem('fontScale') || '1');
            if (!isNaN(savedScale)) document.documentElement.style.setProperty('--font-scale', savedScale);
        }

        function adjustFont(delta) {
            const cur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--font-scale') || '1');
            let next = Math.min(1.6, Math.max(0.8, cur + delta));
            document.documentElement.style.setProperty('--font-scale', next);
            localStorage.setItem('fontScale', String(next));
        }

        // helpers (top-level so filters and details can share)
        function fmtVal(v) {
            if (Array.isArray(v)) return v.length ? v.join('; ') : '—';
            if (v === null || v === undefined || v === '') return '—';
            if (typeof v === 'boolean') return v ? 'true' : 'false';
            if (typeof v === 'string') return v.replaceAll('_',' ');
            return String(v);
        }

        function criticalToEnglish(key, val) {
            if (val == null || val === '') return '—';
            switch (key) {
                case 'boiling_timing':
                    if (val === 'after_writing') return 'boil after writing';
                    if (val === 'before_writing') return 'boil before writing';
                    return `boiling timing: ${fmtVal(val)}`;
                case 'drying_method':
                    if (val === 'sun') return 'sun-dry writing';
                    return `drying method: ${fmtVal(val)}`;
                case 'soaking_medium':
                    if (val === 'brine') return 'brine soak';
                    return `soak in ${fmtVal(val)}`;
                case 'soaking_duration':
                    if (val === 'unspecified') return 'soaking duration: unspecified';
                    return `soaking duration: ${fmtVal(val)}`;
                default:
                    return fmtVal(val);
            }
        }

        function mapCriticalVariant(key, val) {
            if (!val || val === 'unspecified') return null;
            switch (key) {
                case 'boiling_timing':
                    return val === 'after_writing' ? 'boil after writing' : (val === 'before_writing' ? 'boil before writing' : `boiling timing: ${fmtVal(val)}`);
                case 'drying_method':
                    return val === 'sun' ? 'sun-dry writing' : `drying: ${fmtVal(val)}`;
                case 'soaking_medium':
                    return val === 'brine' ? 'brine soak' : `soak in ${fmtVal(val)}`;
                case 'soaking_duration':
                    return `soaking duration: ${fmtVal(val)}`;
                default:
                    return `${key.replaceAll('_',' ')}: ${fmtVal(val)}`;
            }
        }

        function getOverallConfidence(recipe) {
            try {
                const a = recipe && typeof recipe.confidence !== 'undefined' && recipe.confidence !== null && recipe.confidence > 0 ? Number(recipe.confidence) : undefined;
                const b = recipe && recipe.full_data && recipe.full_data.analysis_confidence && typeof recipe.full_data.analysis_confidence.overall_confidence !== 'undefined'
                    ? Number(recipe.full_data.analysis_confidence.overall_confidence)
                    : undefined;
                const v = (isFinite(a) && a > 0) ? a : (isFinite(b) ? b : 0);

                if (!isFinite(v)) return 0;
                return Math.min(Math.max(v, 0), 1);
            } catch (err) {
                console.error('Error in getOverallConfidence:', err);
                return 0;
            }
        }

        function hasConfidenceData(recipe) {
            try {
                if (recipe && recipe.confidence !== undefined && recipe.confidence !== null) return true;
                const ac = recipe && recipe.full_data && recipe.full_data.analysis_confidence;
                if (!ac) return false;
                if (ac.overall_confidence !== undefined && ac.overall_confidence !== null) return true;
                const keys = ['text_completeness','extraction_reliability','relationship_indicators','linguistic_analysis'];
                return keys.some(k => typeof ac[k] === 'number' && isFinite(ac[k]));
            } catch (_) {
                return false;
            }
        }

        async function init() {
            renderSkeleton(8);
            await loadRecipes();
            populateCheckboxes();
            setupEventListeners();
            setupFilterToggles();

            // Set default sort to date ascending
            document.getElementById('orderBy').value = 'date_asc';

            applyFilters();
            initThemeAndFont();
        }

        async function loadRecipes() {
            try {
                // Load from GitHub Pages data
                const dataUrl = new URL('data/witnesses.json', window.location.href).href;
                const response = await fetch('data/witnesses.json');
                if (response.ok) {
                    const data = await response.json();
                    recipes = transformDataForWeb(data);
                    return;
                } else {
                    console.error('Response not ok:', response.status, response.statusText);
                }
            } catch (e) {
                console.error('Failed to load recipes:', e);
            }

            // Fallback sample data if needed
            recipes = [
                {
                    witness_id: "W01",
                    date: 1000,
                    author: "Constantinus VII, Cassianus Bassus",
                    language: "Greek",
                    genre: "Agriculture / House Economy",
                    source_work: "Laur. Plut. 59.32, Geoponikon",
                    ingredients: ["galls", "alum", "vinegar", "wax"],
                    gall_presence: "present",
                    confidence: 0.96,
                    process_summary: "Grind galls and alum with vinegar, write on egg, dry in sun, soak in brine, boil",
                    attribution: "Africanus"
                }
            ];
        }

        // Transform the detailed JSON structure to the simplified format expected by the web interface
        function transformDataForWeb(data) {
            return data.map(item => {
                const transformed = {
                    witness_id: item.metadata?.witness_id || 'Unknown',
                    date: item.metadata?.date || 0,
                    author: item.metadata?.author || 'Anonymous',
                    language: item.metadata?.language || 'unknown',
                    genre: item.metadata?.genre || 'unknown',
                    source_work: item.metadata?.source_work || 'Unknown Source',
                    ingredients: item.ingredients?.primary_components?.map(c => c.substance) || [],
                    gall_presence: item.ingredients?.diagnostic_variants?.gall_presence || 'unknown',
                    confidence: item.confidence || item.analysis_confidence?.overall_confidence || 0,
                    process_summary: item.process_summary || 'Process details available',
                    attribution: item.attribution || 'unknown',
                    full_data: item // Keep full data for detailed analysis
                };

                return transformed;
            });
        }

        function populateCheckboxes() {
            const centuries = Array.from(new Set(recipes.map(r => Math.floor(r.date / 100) + 1))).sort((a,b)=>a-b);
            renderCheckboxList('centuryList', centuries.map(c => ({value:String(c), label:`${c}th`})), 'cent');
            const languages = Array.from(new Set(recipes.map(r => r.language))).sort();
            renderCheckboxList('languageList', languages.map(v => ({value:v, label:v})), 'lang');
            const genres = Array.from(new Set(recipes.map(r => r.genre))).sort();
            renderCheckboxList('genreList', genres.map(v => ({value:v, label:v})), 'genre');

            // Ingredient Family filter
            const ingredientFamilies = ['Gall and Alum Family', 'Alum Only Family', 'Other'];
            renderCheckboxList('ingredientFamilyList', ingredientFamilies.map(v => ({value:v, label:v})), 'ingredientFamily');

            // Extract all unique ingredients from recipes
            const ingredientsSet = new Set();
            recipes.forEach(r => {
                if (Array.isArray(r.ingredients)) {
                    r.ingredients.forEach(ing => ingredientsSet.add(ing));
                }
            });
            const ingredients = Array.from(ingredientsSet).sort();
            renderCheckboxList('ingredientList', ingredients.map(v => ({value:v, label:v})), 'ingredient');

            const boilSet = new Set();
            const drySet = new Set();
            const soakMediumSet = new Set();
            const soakDurationSet = new Set();
            recipes.forEach(r => {
                const cv = (r.full_data && r.full_data.process_steps && r.full_data.process_steps.critical_variants) || {};
                if (cv.boiling_timing != null && cv.boiling_timing !== '') boilSet.add(String(cv.boiling_timing));
                if (cv.drying_method != null && cv.drying_method !== '') drySet.add(String(cv.drying_method));
                if (cv.soaking_medium != null && cv.soaking_medium !== '') soakMediumSet.add(String(cv.soaking_medium));
                if (cv.soaking_duration != null && cv.soaking_duration !== '') soakDurationSet.add(String(cv.soaking_duration));
            });
            renderCheckboxList('boilList', Array.from(boilSet).map(v => ({value:v, label:criticalToEnglish('boiling_timing', v)})), 'boil');
            renderCheckboxList('dryList', Array.from(drySet).map(v => ({value:v, label:criticalToEnglish('drying_method', v)})), 'dry');
            renderCheckboxList('soakMediumList', Array.from(soakMediumSet).map(v => ({value:v, label:criticalToEnglish('soaking_medium', v)})), 'soakMedium');
            renderCheckboxList('soakDurationList', Array.from(soakDurationSet).map(v => ({value:v, label:criticalToEnglish('soaking_duration', v)})), 'soakDuration');
        }

        function setupEventListeners() {
            document.getElementById('orderBy').addEventListener('change', applyFilters);
            document.getElementById('searchInput').addEventListener('input', applyFilters);
            const prev = document.getElementById('prevBtn');
            const next = document.getElementById('nextBtn');
            if (prev) prev.addEventListener('click', () => navigate(-1));
            if (next) next.addEventListener('click', () => navigate(1));
            const inc = document.getElementById('fontInc');
            const dec = document.getElementById('fontDec');
            if (inc) inc.addEventListener('click', () => adjustFont(0.1));
            if (dec) dec.addEventListener('click', () => adjustFont(-0.1));
            // Theme toggle is handled by theme.js (setupThemeToggle)
            const resetBtn = document.getElementById('resetFilters');
            if (resetBtn) resetBtn.addEventListener('click', resetAllFilters);

            // Keyboard navigation: left/right to cycle recipes
            document.addEventListener('keydown', (e) => {
                const tag = (e.target && e.target.tagName) || '';
                if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || e.isComposing) return;
                if (e.key === 'ArrowLeft') { e.preventDefault(); navigate(-1); }
                if (e.key === 'ArrowRight') { e.preventDefault(); navigate(1); }
                if (e.key === 'Escape') {
                    const modal = document.getElementById('recipeModal');
                    if (modal && modal.style.display === 'block') {
                        e.preventDefault();
                        closeModal();
                    }
                }
            });
        }

        function resetAllFilters() {
            // Clear all selected filters
            selected.centuries.clear();
            selected.languages.clear();
            selected.genres.clear();
            selected.ingredientFamily.clear();
            selected.ingredients.clear();
            selected.boil.clear();
            selected.dry.clear();
            selected.soakMedium.clear();
            selected.soakDuration.clear();

            // Reset form controls
            document.getElementById('searchInput').value = '';
            document.getElementById('orderBy').value = 'date_asc';

            // Uncheck all checkboxes
            document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });

            // Update filter counts
            ['cent', 'lang', 'genre', 'ingredientFamily', 'ingredient', 'boil', 'dry', 'soakMedium', 'soakDuration'].forEach(prefix => {
                updateFilterCount(prefix);
            });

            // Close all expanded filters
            document.querySelectorAll('.filter-toggle').forEach(t => {
                t.classList.remove('expanded');
                t.setAttribute('aria-expanded', 'false');
            });
            document.querySelectorAll('.filter-content').forEach(c => {
                c.classList.remove('expanded');
                c.setAttribute('hidden', '');
            });

            // Apply filters to show all results
            applyFilters();
        }

        // Comprehensive search function that searches all fields in recipe data
        function searchAllFields(obj, searchTerm) {
            if (!obj || !searchTerm) return false;

            searchTerm = searchTerm.toLowerCase();

            // Recursively search through all object properties
            function searchObject(item) {
                if (item === null || item === undefined) return false;

                // Handle strings
                if (typeof item === 'string') {
                    return item.toLowerCase().includes(searchTerm);
                }

                // Handle numbers (convert to string for search)
                if (typeof item === 'number') {
                    return String(item).includes(searchTerm);
                }

                // Handle arrays
                if (Array.isArray(item)) {
                    return item.some(element => searchObject(element));
                }

                // Handle objects
                if (typeof item === 'object') {
                    return Object.values(item).some(value => searchObject(value));
                }

                return false;
            }

            return searchObject(obj);
        }

        function applyFilters() {
            const orderBy = document.getElementById('orderBy').value;
            const search = document.getElementById('searchInput').value.toLowerCase();

            filteredRecipes = recipes.filter(r => {
                const c = Math.floor(r.date / 100) + 1;
                const cv = (r.full_data && r.full_data.process_steps && r.full_data.process_steps.critical_variants) || {};
                const matchesCent = selected.centuries.size === 0 || selected.centuries.has(String(c));
                const matchesLang = selected.languages.size === 0 || selected.languages.has(r.language);
                const matchesGenre = selected.genres.size === 0 || selected.genres.has(r.genre);

                // Check ingredient family
                const ingredientFamily = getIngredientFamily(r);
                const matchesIngredientFamily = selected.ingredientFamily.size === 0 || selected.ingredientFamily.has(ingredientFamily);

                // Check if recipe has any of the selected ingredients
                const matchesIngredient = selected.ingredients.size === 0 ||
                    (Array.isArray(r.ingredients) && r.ingredients.some(ing => selected.ingredients.has(ing)));

                const matchesBoil = selected.boil.size === 0 || selected.boil.has(String(cv.boiling_timing || ''));
                const matchesDry = selected.dry.size === 0 || selected.dry.has(String(cv.drying_method || ''));
                const matchesSoakM = selected.soakMedium.size === 0 || selected.soakMedium.has(String(cv.soaking_medium || ''));
                const matchesSoakD = selected.soakDuration.size === 0 || selected.soakDuration.has(String(cv.soaking_duration || ''));
                const matchesSearch = !search || searchAllFields(r.full_data || r, search);
                return matchesCent && matchesLang && matchesGenre && matchesIngredientFamily && matchesIngredient && matchesBoil && matchesDry && matchesSoakM && matchesSoakD && matchesSearch;
            });

            switch(orderBy) {
                case 'date_asc': filteredRecipes.sort((a, b) => a.date - b.date); break;
                case 'date_desc': filteredRecipes.sort((a, b) => b.date - a.date); break;
                case 'confidence': filteredRecipes.sort((a, b) => getOverallConfidence(b) - getOverallConfidence(a)); break;
                case 'author': filteredRecipes.sort((a, b) => (a.author || '').localeCompare(b.author || '')); break;
            }
            displayRecipes();
            const count = document.getElementById('resultCount');
            if (count) count.textContent = filteredRecipes.length;
        }

        function displayRecipes() {
            const grid = document.getElementById('recipeGrid');
            const count = document.getElementById('resultCount');

            count.textContent = filteredRecipes.length;

            if (filteredRecipes.length === 0) {
                grid.innerHTML = '<div class="no-results">No recipes found matching your filters.</div>';
                return;
            }

            grid.innerHTML = filteredRecipes.map(recipe => {
                const conf = getOverallConfidence(recipe);
                const hasConf = hasConfidenceData(recipe);
                const ing = Array.isArray(recipe.ingredients) ? recipe.ingredients : [];
                return `
                <a href="recipe.html?id=${recipe.witness_id}&from=database" class="recipe-card recipe-card-link">
                    <div class="recipe-header">
                        <div class="recipe-title">${recipe.source_work || 'Historical Recipe'}</div>
                        <div class="recipe-date">${recipe.date} CE</div>
                        <div class="recipe-author">${recipe.author || 'Anonymous'}</div>
                        <span class="recipe-genre">${recipe.genre}</span>
                    </div>
                    ${ing.length ? `<div class="recipe-ingredients">${ing.map(i => `<span class="ingredient">${i}</span>`).join('')}</div>` : ''}
                    <div class="process-summary">${recipe.process_summary || 'Process details available in analysis'}</div>
                    <div class="confidence-meter" title="Analysis Confidence: ${hasConf ? (conf * 100).toFixed(0) + '%' : 'not assessed'}">
                        <div class="confidence-fill" style="width: ${hasConf ? (conf * 100) : 0}%"></div>
                        <div class="confidence-label">${hasConf ? (conf * 100).toFixed(0) + '%' : 'n/a'}</div>
                    </div>
                    <div class="witness-id-footer">Witness ID: ${recipe.witness_id}</div>
                </a>
            `}).join('');
        }

        let _modalFocusTrapCleanup = null;
        let _modalLastFocused = null;

        function showDetails(witnessId) {
            const recipe = recipes.find(r => r.witness_id === witnessId);
            if (!recipe) return;
            currentIndex = filteredRecipes.findIndex(r => r.witness_id === witnessId);

            const modal = document.getElementById('recipeModal');
            const modalBody = document.getElementById('modalBody');

            // helpers for plain-language rendering (defined top-level)

            let modalContent = `
                <h2 id="recipeModalTitle">${recipe.witness_id}: ${recipe.source_work}
                    <span class="language-badge">${recipe.language}</span>
                </h2>

                <div class="detail-section">
                    <h3>Metadata</h3>
                    <p><strong>Date:</strong> ${recipe.date} CE</p>
                    <p><strong>Author:</strong> ${recipe.author || 'Anonymous'}</p>
                    <p><strong>Genre:</strong> ${recipe.genre}</p>
                    ${recipe.attribution ? `<p><strong>Attribution:</strong> ${recipe.attribution}</p>` : ''}
                    ${recipe.full_data && recipe.full_data.text_data && recipe.full_data.text_data.url && recipe.full_data.text_data.url !== '[URL Missing]'
                        ? `<p><strong>URL:</strong> <a href="${recipe.full_data.text_data.url}" target="_blank" style="color: #d4af37;">${recipe.full_data.text_data.url}</a></p>`
                        : ''}
                </div>
            `;

            // Add full text if available
            if (recipe.full_data && recipe.full_data.text_data) {
                const textData = recipe.full_data.text_data;
                if (textData.full_text) {
                    modalContent += `
                        <div class="detail-section">
                            <h3>Full Text</h3>
                            <div class="full-text">${textData.full_text}</div>
                        </div>
                    `;
                }
                if (textData.translation) {
                    modalContent += `
                        <div class="detail-section">
                            <h3>Translation</h3>
                            <div class="translation">${textData.translation}</div>
                        </div>
                    `;
                }
            }

            // Add ingredients detail
            modalContent += `
                <div class="detail-section">
                    <h3>Ingredients</h3>
                    ${(Array.isArray(recipe.ingredients) ? recipe.ingredients : []).map(i => `<span class=\"ingredient\">${i}</span>`).join(' ')}
                    <p class="mt-8"><strong>Galls Present:</strong> ${recipe.gall_presence}</p>
                </div>
            `;

            // Add detailed ingredients if available
            if (recipe.full_data && recipe.full_data.ingredients_detailed) {
                const ingredients = recipe.full_data.ingredients_detailed;
                if (ingredients.primary_components && ingredients.primary_components.length > 0) {
                    modalContent += `
                        <div class="detail-section">
                            <h3 class="collapsible" onclick="toggleCollapsible(this)">Detailed Ingredient Analysis ▼</h3>
                            <div class="collapsible-content">
                    `;

                    ingredients.primary_components.forEach(comp => {
                        modalContent += `
                            <div class="ingredient-detail">
                                <div>
                                    <span class="ingredient-name">${comp.substance}</span>
                                    ${comp.quantity ? ` (${comp.quantity} ${comp.measurement_system || ''})` : ''}
                                </div>
                                <div class="ingredient-phrasing">${comp.original_phrasing || ''}</div>
                            </div>
                        `;
                    });

                    modalContent += `</div></div>`;
                }
            }

            // Add process steps
            if (recipe.full_data && recipe.full_data.process_steps) {
                const processSteps = recipe.full_data.process_steps.preparation_sequence;
                const critVars = (recipe.full_data.process_steps.critical_variants) || {};
                const toolSpecs = (recipe.full_data.process_steps.tool_specifications) || {};
                if (processSteps && processSteps.length > 0) {
                    modalContent += `
                        <div class="detail-section">
                            <h3 class="collapsible" onclick="toggleCollapsible(this)">Process Steps ▼</h3>
                            <div class="collapsible-content">
                    `;

                    processSteps.forEach((step, index) => {
                        modalContent += `
                            <div class="process-step">
                                <div class="step-number">Step ${step.step_number || index + 1}: ${step.action || ''}</div>
                                <p>${step.details || ''}</p>
                                ${step.original_phrasing ? `<p class="ingredient-phrasing">Original: "${step.original_phrasing}"</p>` : ''}
                            </div>
                        `;
                    });

                    modalContent += `</div></div>`;
                }

                // Critical variants (plain language)
                const criticalLines = [];
                Object.entries(critVars).forEach(([k, v]) => {
                    const text = mapCriticalVariant(k, v);
                    if (text) criticalLines.push(text);
                });
                if (Array.isArray(critVars.temperature_specifications) && critVars.temperature_specifications.length) {
                    criticalLines.push(`temperature: ${critVars.temperature_specifications.join('; ')}`);
                }
                if (criticalLines.length) {
                    modalContent += `
                        <div class="detail-section">
                            <h3>Critical Variants</h3>
                            <ul style="margin-left: 18px; list-style: disc;">
                                ${criticalLines.map(t => `<li>${t}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
            } else {
                modalContent += `
                    <div class="detail-section">
                        <h3>Process Summary</h3>
                        <p>${recipe.process_summary}</p>
                    </div>
                `;
            }

            // Relationship Analysis
            if (recipe.full_data && recipe.full_data.relationship_analysis) {
                const ra = recipe.full_data.relationship_analysis;
                const dci = ra.direct_copy_indicators || {};
                const tm = ra.translation_markers || {};
                const cs = ra.contamination_signals || {};
                const gam = ra.genre_adaptation_markers || {};

                let relHTML = '';
                // Direct Copy Indicators
                if (Object.keys(dci).length) {
                    relHTML += `
                        <div class="detail-subsection">
                            <h4>Direct Copy Indicators</h4>
                            ${Array.isArray(dci.verbatim_sections) ? `<p><strong>Verbatim sections:</strong> ${dci.verbatim_sections.length ? dci.verbatim_sections.join('; ') : '—'}</p>` : ''}
                            ${Array.isArray(dci.shared_errors) ? `<p><strong>Shared errors:</strong> ${dci.shared_errors.length ? dci.shared_errors.join('; ') : '—'}</p>` : ''}
                            ${dci.probability != null ? `<p><strong>Probability:</strong> ${(dci.probability*100).toFixed(1)}%</p>` : ''}
                        </div>
                    `;
                }
                // Translation Markers
                if (Object.keys(tm).length) {
                    relHTML += `
                        <div class="detail-subsection">
                            <h4>Translation Markers</h4>
                            ${tm.source_language_evidence != null ? `<p><strong>Source language evidence:</strong> ${fmtVal(tm.source_language_evidence)}</p>` : ''}
                            ${tm.translation_generation != null ? `<p><strong>Translation generation:</strong> ${fmtVal(tm.translation_generation)}</p>` : ''}
                            ${Array.isArray(tm.parallel_translation_indicators) ? `<p><strong>Parallel translation indicators:</strong> ${tm.parallel_translation_indicators.length ? tm.parallel_translation_indicators.join('; ') : '—'}</p>` : ''}
                        </div>
                    `;
                }
                // Contamination Signals
                if (Object.keys(cs).length) {
                    relHTML += `
                        <div class="detail-subsection">
                            <h4>Contamination Signals</h4>
                            ${Array.isArray(cs.mixed_characteristics) ? `<p><strong>Mixed characteristics:</strong> ${cs.mixed_characteristics.length ? cs.mixed_characteristics.join('; ') : '—'}</p>` : ''}
                            ${Array.isArray(cs.secondary_influence) ? `<p><strong>Secondary influence:</strong> ${cs.secondary_influence.length ? cs.secondary_influence.join('; ') : '—'}</p>` : ''}
                            ${cs.anomaly_level != null ? `<p><strong>Anomaly level:</strong> ${fmtVal(cs.anomaly_level)}</p>` : ''}
                        </div>
                    `;
                }
                // Genre Adaptation Markers (Contextual modifications, Audience targeting)
                if (Object.keys(gam).length) {
                    relHTML += `
                        <div class="detail-subsection">
                            <h4>Genre Adaptation Markers</h4>
                            ${Array.isArray(gam.register_shifts) ? `<p><strong>Register shifts:</strong> ${gam.register_shifts.length ? gam.register_shifts.join('; ') : '—'}</p>` : ''}
                            ${Array.isArray(gam.contextual_modifications) ? `<p><strong>Contextual modifications:</strong> ${gam.contextual_modifications.length ? gam.contextual_modifications.join('; ') : '—'}</p>` : ''}
                            ${Array.isArray(gam.audience_targeting) ? `<p><strong>Audience targeting:</strong> ${gam.audience_targeting.length ? gam.audience_targeting.join('; ') : '—'}</p>` : ''}
                        </div>
                    `;
                }
                if (relHTML) {
                    modalContent += `
                        <div class="detail-section">
                            <h3 class="collapsible" onclick="toggleCollapsible(this)">Relationship Analysis ▼</h3>
                            <div class="collapsible-content">${relHTML}</div>
                        </div>
                    `;
                }
            }

            // Add confidence
            const overallConf = getOverallConfidence(recipe);
            const hasConf = hasConfidenceData(recipe);
            modalContent += `
                <div class="detail-section">
                    <h3>Analysis Confidence</h3>
                    <div class="confidence-meter">
                        <div class="confidence-fill" style="width: ${hasConf ? overallConf * 100 : 0}%"></div>
                        <div class="confidence-label">${hasConf ? (overallConf * 100).toFixed(1) + '%' : 'not assessed'}</div>
                    </div>
                    ${hasConf ? `<p class=\"mt-8\">${(overallConf * 100).toFixed(1)}% confidence in analysis</p>` : `<p class=\"mt-8\">No confidence assessment available</p>`}
                    ${recipe.full_data && recipe.full_data.analysis_confidence && Array.isArray(recipe.full_data.analysis_confidence.uncertainty_flags) && recipe.full_data.analysis_confidence.uncertainty_flags.length
                        ? `<div class=\"mt-8\"><strong>Uncertainty flags:</strong> ${recipe.full_data.analysis_confidence.uncertainty_flags.join('; ')}</div>`
                        : ''}
                </div>
            `;

            modalBody.innerHTML = modalContent;
            modal.style.display = 'block';
            // Focus trap
            _modalLastFocused = document.activeElement;
            _modalFocusTrapCleanup = enableFocusTrap(modal);
        }

        function toggleCollapsible(element) {
            element.classList.toggle('active');
            const content = element.nextElementSibling;
            if (element.innerHTML.includes('▼')) {
                element.innerHTML = element.innerHTML.replace('▼', '▲');
            } else {
                element.innerHTML = element.innerHTML.replace('▲', '▼');
            }
        }

        function closeModal() {
            const modal = document.getElementById('recipeModal');
            modal.style.display = 'none';
            if (typeof _modalFocusTrapCleanup === 'function') {
                _modalFocusTrapCleanup();
                _modalFocusTrapCleanup = null;
            }
            if (_modalLastFocused && _modalLastFocused.focus) {
                _modalLastFocused.focus();
            }
        }

        window.addEventListener('click', (event) => {
            const modal = document.getElementById('recipeModal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        });

        // Focus trap utility for modal dialogs
        function enableFocusTrap(container) {
            const selectors = [
                'a[href]', 'button:not([disabled])', 'textarea', 'input', 'select', '[tabindex]:not([tabindex="-1"])'
            ];
            const getFocusable = () => Array.from(container.querySelectorAll(selectors.join(',')))
                .filter(el => el.offsetParent !== null);
            const focusables = getFocusable();
            if (focusables.length) {
                focusables[0].focus();
            } else {
                container.focus({ preventScroll: true });
            }
            const handler = (e) => {
                if (e.key !== 'Tab') return;
                const items = getFocusable();
                if (!items.length) return;
                const first = items[0];
                const last = items[items.length - 1];
                if (e.shiftKey && document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                } else if (!e.shiftKey && document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            };
            container.addEventListener('keydown', handler);
            return () => container.removeEventListener('keydown', handler);
        }

        // Mobile filter toggle functionality
        function setupMobileFilterToggle() {
            const toggleBtn = document.getElementById('mobileFilterToggle');
            const sidebar = document.getElementById('filterSidebar');

            if (toggleBtn && sidebar) {
                toggleBtn.addEventListener('click', () => {
                    const isExpanded = sidebar.classList.contains('mobile-expanded');

                    if (isExpanded) {
                        sidebar.classList.remove('mobile-expanded');
                        toggleBtn.classList.remove('expanded');
                    } else {
                        sidebar.classList.add('mobile-expanded');
                        toggleBtn.classList.add('expanded');
                    }
                });
            }
        }

        setupMobileFilterToggle();
        init();
    
